"""
Defines internal API interaction and AI threading.
"""

from __future__ import annotations

import ctypes
import importlib
import os
import random
import signal
import threading
import traceback
import warnings
from typing import Iterable

import numpy as np
import pygame as pg

import const
import const.map
import model
from api import prototype
from const import DECISION_TICKS, FPS, MAX_TEAMS
from instances_manager import get_model
from model.character.character import CharacterMovingState
from util import log_critical, log_info, log_warning


class GameError(Exception):
    """Exception for internal game error occurs when interacting with API."""

    def __init__(self, message):
        super().__init__("The game broke. This is not your fault. Please contact us so we can fix it." + message)


def enforce_type(name, obj, *args):
    if not isinstance(obj, args):
        types = " | ".join(list(map(lambda x: x.__name__, args)))
        raise TypeError(f"{name} must be type {types}.")


class Internal(prototype.API):
    """
    Internal implementation of API.  
    Please do note everything from internal to API is named `cast` (because we usually just take the fields)
    and everything from API to internal is named `map` (because we need extra map to convert back to original ref)
    """

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

    def __team(self):
        return get_model().teams[self.team_id]

    @classmethod
    def __cast_team_id(cls, index: int):
        """
        AI interprets the team as 1, 2, 3, 4 whereas internal naming uses 0, 1, 2, 3.
        """
        return index + 1

    @classmethod
    def __map_team_id(cls, index: int):
        return index - 1

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
        for _ in range(4):
            self.transform = np.dot(rotate, self.transform)
            transformed = np.dot(self.transform, respect)
            if np.linalg.norm(transformed) < best:
                best = np.linalg.norm(transformed)
        for _ in range(4):
            self.transform = np.dot(rotate, self.transform)
            transformed = np.dot(self.transform, respect)
            if abs(np.linalg.norm(transformed) - best) < EPS:
                break

    def __transform(self, position: pg.Vector2, is_position: bool, inverse: bool = False):
        """
        Transform internal positions into real math positions.
        """
        if self.transform is None:
            self.__build_transform_matrix()

        vector = np.array([[position.x],
                           [position.y],
                           [1 if is_position else 0]])
        vector = np.dot(np.linalg.inv(self.transform) if inverse else self.transform,
                        vector)
        return pg.Vector2(vector[0][0], vector[1][0])

    @classmethod
    def __map_character_type(cls, class_type: prototype.CharacterClass):
        """
        Map API character type to internal type.
        """
        if class_type == prototype.CharacterClass.MELEE:
            return const.CharacterType.MELEE
        if class_type == prototype.CharacterClass.RANGER:
            return const.CharacterType.RANGER
        if class_type == prototype.CharacterClass.SNIPER:
            return const.CharacterType.SNIPER
        raise ValueError

    def __convert_character(self, internal: model.Character) -> prototype.Character:
        """
        Convert a `model.Character` to `api.Character`.
        """
        character_class = prototype.CharacterClass.UNKNOWN
        if isinstance(internal, model.Melee):
            character_class = prototype.CharacterClass.MELEE
        elif isinstance(internal, model.Ranger):
            character_class = prototype.CharacterClass.RANGER
        elif isinstance(internal, model.Sniper):
            character_class = prototype.CharacterClass.SNIPER
        else:
            raise GameError("Unknown character type")
        extern = prototype.Character(
            _id=internal.id,
            _type=character_class,
            _position=self.__transform(internal.position, is_position=True),
            _speed=internal.attribute.attack_speed,
            _attack_range=internal.attribute.attack_range,
            _damage=internal.attribute.attack_damage,
            _vision=internal.attribute.vision,
            _health=internal.health,
            _max_health=internal.attribute.max_health,
            _team_id=Internal.__cast_team_id(internal.team.team_id)
        )
        return extern

    def __convert_tower(self, internal: model.Tower) -> prototype.Tower:
        """
        Convert a `model.Tower` to `api.Tower`
        """
        character_class = prototype.CharacterClass.UNKNOWN
        if internal.character_type == const.CharacterType.MELEE:
            character_class = prototype.CharacterClass.MELEE
        elif internal.character_type == const.CharacterType.RANGER:
            character_class = prototype.CharacterClass.RANGER
        elif internal.character_type == const.CharacterType.SNIPER:
            character_class = prototype.CharacterClass.SNIPER
        else:
            raise GameError("Unknown spawn character type")
        extern = prototype.Tower(
            _id=internal.id,
            _position=self.__transform(internal.position, is_position=True),
            _period=internal.period,
            _is_fountain=internal.is_fountain,
            _attack_range=internal.attribute.attack_range,
            _damage=internal.attribute.attack_damage,
            _vision=internal.attribute.vision,
            _health=internal.health,
            _max_health=internal.attribute.max_health,
            _team_id=0 if internal.team is None else Internal.__cast_team_id(
                internal.team.team_id),
            _spwan_character_type=character_class
        )
        return extern

    def __register_character(self, internal: model.Character) -> prototype.Character:
        """
        Register a `model.Character` to `api.Character`.
        Therefore, API can only manipulate a character using the given interface
        while we still know the original `model.Character`.  
        If multiple instance are registered during the same AI decision call, 
        they will be all valid for operations.
        """
        extern = self.__convert_character(internal)
        self.__character_map[internal.id] = extern
        self.__reverse_character_map[id(extern)] = internal
        return self.__character_map[internal.id]

    def __register_tower(self, internal: model.Tower) -> prototype.Tower:
        """
        Register a `model.Tower` to `api.Tower` like above.
        """
        extern = self.__convert_tower(internal)
        self.__tower_map[internal.id] = extern
        self.__reverse_tower_map[id(extern)] = internal
        return self.__tower_map[internal.id]

    def __access_character(self, extern: prototype.Character) -> model.Character:
        """
        Return registered character. None if it does not exist.
        """
        if id(extern) not in self.__reverse_character_map:
            log_warning(
                f"[AI] AI of team {self.team_id} used invalid prototype.Character. Maybe it is already expired.")
            return None
        return self.__reverse_character_map[id(extern)]

    def __access_tower(self, extern: prototype.Tower) -> model.Tower:
        """
        Return registered tower. None if it does not exist.
        """
        if id(extern) not in self.__reverse_tower_map:
            log_warning(
                f"[AI] AI of team {self.team_id} used invalid prototype.Tower. Maybe it is already expired.")
            return None
        return self.__reverse_tower_map[id(extern)]

    def __is_controllable(self, obj: None | model.Character | model.Tower):
        return (obj is not None and
                obj.team == self.__team() and
                obj.health > 0)

    """Methods defined below are all callable from AI."""

    def get_current_time(self):
        return get_model().get_time()

    def get_grid_size(self):
        return const.ARENA_SIZE[0]

    def get_owned_characters(self) -> list[prototype.Character]:
        with self.__team().character_lock:
            return sorted([self.__register_character(character)
                           for character in self.__team().character_list if character.health > 0],
                          key=lambda x: x.id)

    def get_owned_towers(self) -> list[prototype.Tower]:
        with self.__team().tower_lock:
            return sorted([self.__register_tower(tower)
                           for tower in self.__team().towers],
                          key=lambda x: x.id)

    def get_team_id(self) -> int:
        return Internal.__cast_team_id(self.__team().team_id)

    def get_score_of_team(self, index=None) -> int:
        enforce_type('index', index, int, type(None))

        if index is None:
            index = self.team_id
        if index < 0 or index >= MAX_TEAMS:
            raise IndexError
        team = get_model().teams[index]
        # Should be correct, if model implementation changes this should fail
        if not team.team_id == index:
            log_critical("[API] Team ID mismatch: team.team_id, index")
            raise GameError("Team ID implement has changed.")
        return team.points

    def get_visible_characters(self) -> list[prototype.Character]:
        vision = self.__team().vision
        entities = []
        with get_model().entity_lock:
            entities = get_model().entities.copy()
        character_list: list[prototype.Character] = [
            self.__register_character(entity) for entity in entities
            if (isinstance(entity, model.Character) and
                vision.entity_inside_vision(entity)) and
            entity.health > 0]
        return sorted(character_list, key=lambda x: x.id)

    def get_visible_towers(self) -> list[prototype.Tower]:
        vision = self.__team().vision
        entities = []
        with get_model().entity_lock:
            entities = get_model().entities.copy()
        tower_list: list[prototype.Tower] = [
            self.__register_tower(entity) for entity in entities
            if (isinstance(entity, model.Tower) and
                vision.entity_inside_vision(entity)) and
            entity.health > 0]
        return sorted(tower_list, key=lambda x: x.id)

    def get_movement(self, character: prototype.Character) -> prototype.Movement:
        character: model.Character = self.__access_character(character)
        if not self.__is_controllable(character):
            return prototype.Movement(prototype.MovementStatusClass.UNKNOWN)
        with character.moving_lock:
            if character.move_state == CharacterMovingState.STOPPED:
                return prototype.Movement(prototype.MovementStatusClass.STOPPED)
            if character.move_state == CharacterMovingState.TO_DIRECTION:
                return prototype.Movement(prototype.MovementStatusClass.TO_DIRECTION,
                                          self.__transform(character.move_direction.normalize(), is_position=False))
            if character.move_state == CharacterMovingState.TO_POSITION:
                return prototype.Movement(prototype.MovementStatusClass.TO_POSITION,
                                          self.__transform(character.move_destination, is_position=True))

    def refresh_character(self, character: prototype.Character) -> prototype.Character | None:
        internal = self.__access_character(character)
        if internal is None or not internal.alive:
            return None
        return self.__register_character(internal)

    def refresh_tower(self, tower: prototype.Tower) -> prototype.Tower | None:
        internal = self.__access_tower(tower)
        if internal is None or not internal.alive:
            return None
        return self.__register_tower(tower)

    def get_visibility(self) -> list[list[int]]:
        mask = self.__team().vision.mask
        vision_grid = pg.surfarray.array_alpha(mask)
        vision_grid[vision_grid == 0] = 1
        vision_grid[vision_grid == 255] = 0
        # Upside down flip
        vision_grid = np.flip(vision_grid, axis=0)
        if self.transform is None:
            self.__build_transform_matrix()
        # Rotate visibility matrix base on transform
        vision_grid = np.rot90(vision_grid, 3)
        if self.transform[0][0] == 0 and self.transform[0][1] == 1:
            vision_grid = np.rot90(vision_grid)
        elif self.transform[0][0] == -1 and self.transform[0][1] == 0:
            vision_grid = np.rot90(vision_grid, 2)
        elif self.transform[0][0] == 0 and self.transform[0][1] == -1:
            vision_grid = np.rot90(vision_grid, 3)
        return vision_grid.tolist()

    def is_visible(self, position: pg.Vector2) -> bool:
        return self.__team().vision.position_inside_vision(
            self.__transform(position, is_position=True, inverse=True))

    def get_terrain(self, position: pg.Vector2) -> prototype.MapTerrain:
        W = const.ARENA_SIZE[1]
        if position.x < 0 or position.x > W or position.y < 0 or position.x > W:
            return prototype.MapTerrain.OUT_OF_BOUNDS
        terrain = get_model().map.get_position_type(self.__transform(position, is_position=True, inverse=True))
        if terrain == const.map.MAP_ROAD:
            return prototype.MapTerrain.ROAD
        if terrain == const.map.MAP_PUDDLE:
            return prototype.MapTerrain.OFFROAD
        if terrain == const.map.MAP_OBSTACLE:
            return prototype.MapTerrain.OBSTACLE
        raise GameError("Unkown terrain type.")

    def action_move_along(self, characters: Iterable[prototype.Character], direction: pg.Vector2):
        enforce_type('characters', characters, Iterable)
        enforce_type('direction', direction, pg.Vector2)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        direction = self.__transform(direction, is_position=False, inverse=True)
        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            with inter.moving_lock:
                inter.set_move_direction(direction)

    def action_move_to(self, characters: Iterable[prototype.Character], destination: pg.Vector2):
        enforce_type('characters', characters, Iterable)
        enforce_type('destination', destination, pg.Vector2)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        destination = self.__transform(destination, is_position=True, inverse=True)
        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            with inter.moving_lock:
                inter.set_move_stop()
                path = get_model().map.find_path(inter.position, destination)
                if len(path) > 0:
                    inter.set_move_position(path)

    def action_move_clear(self, characters: Iterable[prototype.Character]):
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
            internal.attack(target_internal)

    def action_cast_ability(self, characters: Iterable[prototype.Character]):
        enforce_type('characters', characters, Iterable)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            inter.cast_ability()

    def action_wander(self, characters: Iterable[prototype.Character]):
        enforce_type('characters', characters, Iterable)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            with inter.moving_lock:
                inter.set_move_stop()

                direction = inter.move_direction
                if direction == pg.Vector2(0, 0):
                    direction = pg.Vector2(random.random(), random.random())

                direction = direction.normalize()
                new_direction = pg.Vector2()
                new_direction.from_polar(
                    (direction.as_polar()[0], direction.as_polar()[1] + random.uniform(-20, 20)))

                inter.set_move_direction(new_direction)

    def change_spawn_type(self, tower: prototype.Tower, spawn_type: prototype.CharacterClass):
        """change the type of character the tower spawns"""
        enforce_type('tower', tower, prototype.Tower)
        enforce_type('spawn_type', spawn_type, prototype.CharacterClass)

        internal_tower = self.__access_tower(tower)
        if not self.__is_controllable(internal_tower):
            return

        internal_tower.update_character_type(Internal.__map_character_type(spawn_type))

    def sort_by_distance(self, characters: Iterable[prototype.Character], target: pg.Vector2):
        enforce_type('characters', characters, Iterable)
        enforce_type('target', target, pg.Vector2)
        [enforce_type('element of characters', ch, prototype.Character) for ch in characters]

        # We preform no transform at all, as all transform are just translate and rotate.
        # Length is preserved under these operations.
        characters = sorted(characters, key=lambda ch: ch.position.distance_to(target))


class TimeoutException(BaseException):
    """
    Different from builtin `TimeoutError`, this error is not catchable by `except: Exception`.
    It makes more sense for the AI to catch some error without accidentally killed by this exception.
    """


class Timer():
    """
    API Timer thread for killing timed-out AI threads. 
    The timer accepts thread id per timer, which means there should be a timer per AI thread.
    """

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
        """Start the timer."""
        if not self.is_windows:
            # Should be sig, frame but pylint doesn't like it >:(
            def handler(_, __):
                res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(tid), ctypes.py_object(TimeoutException))
                if res != 0:
                    log_warning(f"[API] TimeoutException killed thread {tid}.")

            signal.signal(signal.SIGALRM, handler)

        if not self.is_windows:
            signal.setitimer(signal.ITIMER_REAL, interval)
        else:
            def timeout_alarm(player_id: int):
                log_critical(f"[API] The AI of player {player_id} timed out!")

            self.timer = threading.Timer(interval=interval, function=timeout_alarm,
                                         args=[player_id])
            self.timer.start()
        self.started = True

    def cancel_timer(self):
        """Cancel the timer."""
        try:
            if not self.is_windows:
                signal.setitimer(signal.ITIMER_REAL, 0)
            else:
                self.timer.cancel()
        except TimeoutException:
            log_warning("[API] Perhaps some very slightly timeout.")


helpers = [Internal(i) for i in range(MAX_TEAMS)]
ai = [None] * len(helpers)


def load_ai(files: list[str]):
    """Load AI modules."""
    for i, file in enumerate(files):
        if file == 'human':
            continue
        ai[i] = importlib.import_module('ai.' + file)


def threading_ai(team_id: int, helper: Internal, timer: Timer):
    """Threading AI helper function."""
    # busy wating til timer start, to prevent cancel earlier than start
    while not timer.started:
        pass
    try:
        if ai[team_id] is not None:
            ai[team_id].every_tick(helper)
    except Exception:
        log_critical(f"Caught exception in AI of team {team_id}:\n{traceback.format_exc()}")
    except TimeoutException:
        log_critical(f"[API] AI of team {team_id} timed out!")
    finally:
        timer.cancel_timer()


def start_ai(team_id: int) -> threading.Thread:
    """Start AI thread for one cycle. Returns the AI thread."""
    helpers[team_id].clear()
    timer = Timer()
    t = threading.Thread(target=threading_ai, args=(team_id, helpers[team_id], timer))
    t.start()
    timer.set_timer(1 / FPS * DECISION_TICKS, team_id, t.ident)
    return t
