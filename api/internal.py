from __future__ import annotations

import ctypes
import importlib
import os
import signal
import threading
import traceback
import warnings
from typing import Any, Iterable

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
            _position=internal.position,
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
                _position=internal.position,
                _period=internal.__period,
                _is_fountain=internal.is_fountain,
                _attack_range=internal.attribute.attack_range,
                _damage=internal.attribute.attack_damage,
                _vision=internal.attribute.vision,
                _health=internal.health,
                _max_health=internal.attribute.max_health,
                _team_id=0 if internal.team is None else Internal.__cast_id(internal.team.id),
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

    def get_time(self):
        return get_model().get_time()

    def get_characters(self) -> list[prototype.Character]:
        return [self.__register_character(character)
                for character in self.__team().character_list if character.health > 0]

    def get_towers(self) -> list[prototype.Tower]:
        return [self.__register_tower(tower)
                for tower in self.__team().towers]

    def get_team_id(self) -> int:
        return Internal.__cast_id(self.__team().team_id)

    def get_score(self, index=None) -> int:
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

    def look_characters(self) -> list[prototype.Character]:
        vision = self.__team().vision
        entities = get_model().entities
        character_list: list[prototype.Character] = []
        for entity in entities:
            if not isinstance(entity, model.Tower) and vision.mask.get_at((int(entity.position.x / const.VISION_BLOCK_SIZE), int(entity.position.y / const.VISION_BLOCK_SIZE)))[3] == 0:
                character_list.append(self.__register_character(entity))
        return character_list

    def look_towers(self) -> list[prototype.Tower]:
        vision = self.__team().vision
        entities = get_model().entities
        tower_list: list[prototype.Tower] = []
        for entity in entities:
            if isinstance(entity, model.Tower) and vision.mask.get_at((int(entity.position.x / const.VISION_BLOCK_SIZE), int(entity.position.y / const.VISION_BLOCK_SIZE)))[3] == 0:
                tower_list.append(self.__register_tower(entity))
        return tower_list

    def look_grid(self) -> list[list[bool]]:
        mask = self.__team().vision.mask
        vision_grid = pg.surfarray.array_alpha(mask)
        vision_grid[vision_grid == 0] = 1
        vision_grid[vision_grid == 255] = 0
        return vision_grid.tolist()

    def action_move_along(self, characters: Iterable[prototype.Character], direction: pg.Vector2):
        enforce_type('characters', characters, Iterable)
        enforce_type('direction', direction, pg.Vector2)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        for ch in characters:
            internal = self.__access_character(ch)
            if internal == None:
                continue
            internal.set_move_direction(direction)

    def action_move_to(self, characters: Iterable[prototype.Character], destination: pg.Vector2):
        enforce_type('characters', characters, Iterable)
        enforce_type('destination', destination, pg.Vector2)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if inter != None]
        for inter in internals:
            inter.set_move_stop()
        for inter in internals:
            path = get_model().map.find_path(inter.position, destination)
            inter.set_move_position(path)

    def action_cast_spell(self, characters: Iterable[prototype.Character], target: prototype.Character):
        enforce_type('characters', characters, Iterable)
        enforce_type('target', target, prototype.Character)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        for ch in characters:
            internal = self.__access_character(ch)
            if internal == None:
                continue
            internal.cast_ability()

    def action_attack(self, characters: Iterable[prototype.Character], target: prototype.Character | prototype.Tower):
        enforce_type('characters', characters, Iterable)
        enforce_type('target', target, prototype.Character, prototype.Tower)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        target_internal = None
        if isinstance(target, prototype.Character):
            target_internal = self.__access_character(target)
        elif isinstance(target, prototype.Tower):
            target_internal = self.__access_tower(target)

        for ch in characters:
            internal = self.__access_character(ch)
            if internal is None:
                continue
            internal.attack(target_internal)

    def change_spawn_type(self, tower: model.Tower, spawn_type: prototype.CharacterClass):
        """change the type of character the tower spawns"""
        if not isinstance(spawn_type, prototype.Character):
            raise TypeError("Invalid type of spawn_type.")
        if not isinstance(tower, model.Tower):
            raise TypeError("Invalid type of tower.")
        internal_tower = self.__access_tower(tower)
        if internal_tower is None:
            return

        internal_tower.character_type = spawn_type


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
                    ctypes.c_long(tid), ctypes.py_object(TimeoutError))
                if res != 0:
                    print(f"Tried to raise exception inside a thread, the return value is {res}.")

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
    if ai[team_id] == None:
        return
    # busy wating til timer start, to prevent cancel earlier than start
    while not timer.started:
        pass
    try:
        ai[team_id].every_tick(helper)
    except Exception as e:
        print(f"Caught exception in AI of team {team_id}:")
        print(traceback.format_exc())
        return
    finally:
        timer.cancel_timer()


def start_ai(team_id: int):
    helpers[team_id].clear()
    timer = Timer()
    t = threading.Thread(target=threading_ai, args=(team_id, helpers[team_id], timer))
    t.start()
    timer.set_timer(1 / FPS * DECISION_TICKS, team_id, t.ident)
    return t


def finalize_ai(team_id: int):
    helpers[team_id].finalize_movement()
