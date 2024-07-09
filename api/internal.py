from __future__ import annotations

import ctypes
import importlib
import os
import signal
import threading
import traceback
import warnings
from typing import Any, Iterable

import numpy as np
import pygame as pg

import api.prototype as prototype
import const
import model
import model.character
import model.character.melee
import model.character.ranger
import model.character.sniper
from const import DECISION_TICKS, FPS, MAX_TEAMS
from instances_manager import get_model


class GameError(Exception):
    def __init__(self, message):
        super().__init__("The game broke. This is not your fault. Please contact us so we can fix it." + message)


def enforce_type(name, obj, *args):
    if not isinstance(obj, args):
        types = " | ".join(list(map(lambda x: x.__name__, args)))
        raise TypeError(f"{name} must be type {types}.")


class Internal(prototype.API):
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.transform: np.ndarray = None
        self.__character_map = {}
        self.__tower_map = {}
        self.__reverse_character_map = {}
        self.__reverse_tower_map = {}

    def clear(self):
        self.__character_map = {}
        self.__tower_map = {}
        self.__reverse_character_map = {}
        self.__reverse_tower_map = {}

    @classmethod
    def __cast_id(cls, id: int):
        """
        AI interprets the team as 1, 2, 3, 4 whereas internal naming uses 0, 1, 2, 3.
        """
        return id + 1

    @classmethod
    def __recast_id(cls, id: int):
        return id - 1

    def __build_transform_matrix(self):
        assert const.ARENA_SIZE[0] == const.ARENA_SIZE[1]
        W = const.ARENA_SIZE[1]

        self.transform = np.array([[1, 0, 0],
                                   [0, -1, W],
                                   [0, 0, 1]], dtype=float)
        rotate = np.array([[0, -1, W],
                           [1, 0, 0],
                           [0, 0, 1]])
        fountain_position = self.__team().fountain.position
        respect = np.array([[fountain_position.x],
                            [fountain_position.y],
                            [1]])
        best = 1e9
        EPS = 1e-9
        for i in range(4):
            self.transform = np.dot(rotate, self.transform)
            transformed = np.dot(self.transform, respect)
            if np.linalg.norm(transformed) < best:
                best = np.linalg.norm(transformed)
        for i in range(4):
            self.transform = np.dot(rotate, self.transform)
            transformed = np.dot(self.transform, respect)
            if abs(np.linalg.norm(transformed) - best) < EPS:
                break

    def __transform(self, position: pg.Vector2, is_vector: int, inverse: bool = False):
        """
        Transform internal positions into real math positions.
        """
        if self.transform is None:
            self.__build_transform_matrix()

        vector = np.array([[position.x],
                           [position.y],
                           [0 if is_vector else 1]])
        vector = np.dot(np.linalg.inv(self.transform) if inverse else self.transform,
                        vector)
        return pg.Vector2(vector[0][0], vector[1][0])

    @classmethod
    def __cast_character_type(cls, type: int):
        if type == prototype.CharacterClass.melee:
            return const.CharacterType.MELEE
        elif type == prototype.CharacterClass.ranger:
            return const.CharacterType.RANGER
        elif type == prototype.CharacterClass.sniper:
            return const.CharacterType.SNIPER
        else:
            raise ValueError

    def __convert_character(self, internal: model.Character) -> prototype.Character:
        """
        Convert a `model.Character` to `api.Character`.
        """
        character_class = prototype.CharacterClass.unknown
        if isinstance(internal, model.Melee):
            character_class = prototype.CharacterClass.melee
        elif isinstance(internal, model.Ranger):
            character_class = prototype.CharacterClass.ranger
        elif isinstance(internal, model.Sniper):
            character_class = prototype.CharacterClass.sniper
        else:
            raise GameError("Unknown character type")
        extern = prototype.Character(
            _id=internal.id,
            _type=character_class,
            _position=self.__transform(internal.position, is_vector=False),
            _speed=internal.attribute.attack_speed,
            _attack_range=internal.attribute.attack_range,
            _damage=internal.attribute.attack_damage,
            _vision=internal.attribute.vision,
            _health=internal.health,
            _max_health=internal.attribute.max_health,
            _team_id=Internal.__cast_id(internal.team.team_id)
        )
        return extern

    def __register_character(self, internal: model.Character) -> prototype.Character:
        """
        Register a `model.Character` to `api.Character`.
        Therefore, API can only manipulate a character using the given interface
        while we still know the original `model.Character`.
        """

        if internal.id not in self.__character_map:
            extern = self.__convert_character(internal)
            self.__character_map[internal.id] = extern
            self.__reverse_character_map[id(extern)] = internal
        return self.__character_map[internal.id]

    def __convert_tower(self, internal: model.Tower) -> prototype.Tower:
        """
        Convert a `model.Tower` to `api.Tower`
        """
        if internal.id not in self.__tower_map:
            character_class = prototype.CharacterClass.unknown
            if internal.character_type == const.CharacterType.MELEE:
                character_class = prototype.CharacterClass.melee
            elif internal.character_type == const.CharacterType.RANGER:
                character_class = prototype.CharacterClass.ranger
            elif internal.character_type == const.CharacterType.SNIPER:
                character_class = prototype.CharacterClass.sniper
            else:
                raise GameError("Unknown spawn character type")
            extern = prototype.Tower(
                _id=internal.id,
                _position=self.__transform(internal.position, is_vector=False),
                _period=internal.__period,
                _is_fountain=internal.is_fountain,
                _attack_range=internal.attribute.attack_range,
                _damage=internal.attribute.attack_damage,
                _vision=internal.attribute.vision,
                _health=internal.health,
                _max_health=internal.attribute.max_health,
                _team_id=0 if internal.team is None else Internal.__cast_id(internal.team.team_id),
                _spwan_character_type=character_class
            )
        return extern

    def __register_tower(self, internal: model.Tower) -> prototype.Tower:
        """
        Register a `model.Tower` to `api.Tower` like above.
        """
        if internal.id not in self.__tower_map:
            extern = self.__convert_tower(internal)
            self.__tower_map[internal.id] = extern
            self.__reverse_tower_map[id(extern)] = internal
        return self.__tower_map[internal.id]

    def __access_character(self, extern: prototype.Character) -> model.Character:
        """
        Return registered character. None if it does not exist.
        """
        if id(extern) not in self.__reverse_character_map:
            warnings.warn("Invalid prototype.Character. Maybe it is already expired.")
            return None
        return self.__reverse_character_map[id(extern)]

    def __access_tower(self, extern: prototype.Tower) -> model.Tower:
        """
        Return registered tower. None if it does not exist.
        """
        if id(extern) not in self.__reverse_tower_map:
            warnings.warn("Invalid prototype.Tower. Maybe it is already expired.")
            return None
        return self.__reverse_tower_map[id(extern)]

    def __team(self):
        return get_model().teams[self.team_id]

    def __is_controllable(self, obj: None | model.Character | model.Tower):
        return (obj is not None and
                obj.team == self.__team() and
                obj.health > 0)

    def get_current_time(self):
        return get_model().get_time()

    def get_owned_characters(self) -> list[prototype.Character]:
        return [self.__register_character(character)
                for character in self.__team().character_list if character.health > 0]

    def get_owned_towers(self) -> list[prototype.Tower]:
        return [self.__register_tower(tower)
                for tower in self.__team().towers]

    def get_team_id(self) -> int:
        return Internal.__cast_id(self.__team().team_id)

    def get_score_of_team(self, index=None) -> int:
        enforce_type('index', index, int, type(None))

        if index == None:
            index = self.team_id
        if index < 0 or index >= MAX_TEAMS:
            raise IndexError
        team = get_model().teams[index]
        # Should be correct, if model implementation changes this should fail
        if not team.team_id == index:
            print(team.team_id, index)
            raise GameError("Team ID implement has changed.")
        return team.points

    def get_visible_characters(self) -> list[prototype.Character]:
        vision = self.__team().vision
        entities = get_model().entities
        character_list: list[prototype.Character] = [
            self.__register_character(entity) for entity in entities
            if (isinstance(entity, model.Character) and
                vision.entity_inside_vision(entity)) and
            entity.health > 0]
        return character_list

    def get_visible_towers(self) -> list[prototype.Tower]:
        vision = self.__team().vision
        entities = get_model().entities
        tower_list: list[prototype.Tower] = [
            self.__register_tower(entity) for entity in entities
            if (isinstance(entity, model.Tower) and
                vision.entity_inside_vision(entity)) and
            entity.health > 0]
        return tower_list

    # I don't want to deal with transform yet
    # def get_visibility(self) -> list[list[int]]:
    #     mask = self.__team().vision.mask
    #     vision_grid = pg.surfarray.array_alpha(mask)
    #     vision_grid[vision_grid == 0] = 1
    #     vision_grid[vision_grid == 255] = 0
    #     return vision_grid.tolist()

    def is_visible(self, position: pg.Vector2) -> bool:
        return self.__team().vision.position_inside_vision(self.__transform(position, is_vector=False, inverse=True))

    def action_move_along(self, characters: Iterable[prototype.Character], direction: pg.Vector2):
        enforce_type('characters', characters, Iterable)
        enforce_type('direction', direction, pg.Vector2)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        direction = self.__transform(direction, is_vector=True, inverse=True)
        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            with inter.moving_lock:
                inter.set_move_direction(direction)

    def action_move_to(self, characters: Iterable[prototype.Character], destination: pg.Vector2):
        enforce_type('characters', characters, Iterable)
        enforce_type('destination', destination, pg.Vector2)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        if not self.is_visible(destination):
            print(f"[API] team {self.team_id} tried to move to a point outside of vision!")
            return

        destination = self.__transform(destination, is_vector=False, inverse=True)
        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            with inter.moving_lock:
                inter.set_move_stop()
                path = get_model().map.find_path(inter.position, destination)
                inter.set_move_position(path)

    def action_clear(self, characters: Iterable[prototype.Character]):
        enforce_type('characters', characters, Iterable)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            with inter.moving_lock:
                inter.set_move_stop()

    def action_attack(self, characters: Iterable[prototype.Character], target: prototype.Character | prototype.Tower):
        enforce_type('characters', characters, Iterable)
        enforce_type('target', target, prototype.Character, prototype.Tower)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        target_internal = None
        if isinstance(target, prototype.Character):
            target_internal = self.__access_character(target)
        elif isinstance(target, prototype.Tower):
            target_internal = self.__access_tower(target)

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for internal in internals:
            attackable = internal.attackable(target_internal)
            if attackable == model.CharacterAttackResult.FRIENDLY_FIRE:
                print(f"[API] team {self.team_id} tried to attack themselves.")
            elif attackable == model.CharacterAttackResult.COOLDOWN:
                print(f"[API] team {self.team_id} is attacking too fast!")
            elif attackable == model.CharacterAttackResult.OUT_OF_RANGE:
                print(f"[API] team {self.team_id} is attacking too far!")
            else:
                internal.attack(target_internal)

    def action_cast_spell(self, characters: Iterable[prototype.Character], target: prototype.Character):
        enforce_type('characters', characters, Iterable)
        enforce_type('target', target, prototype.Character)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            inter.cast_ability()

    def change_spawn_type(self, tower: prototype.Tower, spawn_type: prototype.CharacterClass):
        """change the type of character the tower spawns"""
        enforce_type('tower', tower, prototype.Tower)
        enforce_type('spawn_type', spawn_type, prototype.CharacterClass)

        internal_tower = self.__access_tower(tower)
        if not self.__is_controllable(internal_tower):
            return

        internal_tower.update_character_type(Internal.__cast_character_type(spawn_type))

    def sort_by_distance(self, characters: Iterable[prototype.Character], target: pg.Vector2):
        enforce_type('characters', characters, Iterable)
        enforce_type('target', target, pg.Vector2)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]
        target = self.__transform(target, is_vector=False, inverse=True)
        characters = sorted(characters, key=lambda ch: ch.position.distance_to(target))


class TimeoutException(BaseException):
    """
    Different from builtin `TimeoutError`, this error is not catchable by `except: Exception`.
    It makes more sense for the AI to catch some error without accidentally killed by this exception.
    """


class Timer():
    def __init__(self):
        if os.name == 'nt':
            self.is_windows = True
        elif os.name == 'posix':
            self.is_windows = False
        else:  # os.name == 'java' or unknown
            raise OSError
        self.timer = None
        self.started = False
        self.for_player_id = None

    def set_timer(self, interval: float, player_id: int, tid: int):
        if not self.is_windows:
            def handler(sig, frame):
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(tid), ctypes.py_object(TimeoutException))
                if res != 0:
                    print(f"Exception killed thread {tid}.")

            signal.signal(signal.SIGALRM, handler)

        if not self.is_windows:
            signal.setitimer(signal.ITIMER_REAL, interval)
        else:
            def timeout_alarm(player_id: int):
                print(f"The AI of player {player_id} time out!")

            self.timer = threading.Timer(interval=interval, function=timeout_alarm,
                                         args=[player_id])
            self.timer.start()
        self.started = True

    def cancel_timer(self):
        try:
            if not self.is_windows:
                signal.setitimer(signal.ITIMER_REAL, 0)
            else:
                self.timer.cancel()
        except:
            print("Perhaps some very slightly timeout.")


helpers = [Internal(i) for i in range(MAX_TEAMS)]
ai = [None] * len(helpers)


def load_ai(files: list[str]):
    for i, file in enumerate(files):
        if file == 'human':
            continue
        ai[i] = importlib.import_module('ai.' + file)


def threading_ai(team_id: int, helper: Internal, timer: Timer):
    # busy wating til timer start, to prevent cancel earlier than start
    while not timer.started:
        pass
    try:
        if ai[team_id] != None:
            ai[team_id].every_tick(helper)
    except Exception as e:
        print(f"Caught exception in AI of team {team_id}:")
        print(traceback.format_exc())
    except TimeoutException as e:
        print(f"[API] AI of team {team_id} timed out!")
    finally:
        timer.cancel_timer()


def start_ai(team_id: int):
    helpers[team_id].clear()
    timer = Timer()
    t = threading.Thread(target=threading_ai, args=(team_id, helpers[team_id], timer))
    t.start()
    timer.set_timer(1 / FPS * DECISION_TICKS, team_id, t.ident)
    return t
