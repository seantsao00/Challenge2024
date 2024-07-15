"""
Defines internal API interaction and AI threading.
"""

import ctypes
import importlib.util
import os
import signal
import threading
import traceback
from typing import Iterable

import numpy as np
import pygame as pg

import const
import const.map
import model
import model.chat
from api import prototype
from const import DECISION_TICKS, FPS, MAX_TEAMS
from instances_manager import get_model
from model.character.character import CharacterMovingState
from util import log_critical, log_warning


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
        self.__chat_sent = False
        self.__last_chat_time_stamp = float('-inf')
        self.__character_map = {}
        self.__tower_map = {}
        self.__reverse_character_map = {}
        self.__reverse_tower_map = {}

    def clear(self):
        self.__chat_sent = False
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
        w = const.ARENA_SIZE[1]

        self.transform = np.array([[1, 0, 0],
                                   [0, -1, w],
                                   [0, 0, 1]], dtype=float)
        rotate = np.array([[0, -1, w],
                           [1, 0, 0],
                           [0, 0, 1]])
        fountain_position = self.__team().fountain.position
        respect = np.array([[fountain_position.x],
                            [fountain_position.y],
                            [1]])
        best = 1e9
        eps = 1e-9
        for _ in range(4):
            self.transform = np.dot(rotate, self.transform)
            transformed = np.dot(self.transform, respect)
            if np.linalg.norm(transformed) < best:
                best = np.linalg.norm(transformed)
        for _ in range(4):
            self.transform = np.dot(rotate, self.transform)
            transformed = np.dot(self.transform, respect)
            if abs(np.linalg.norm(transformed) - best) < eps:
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
            _attack_speed=1 / internal.attribute.attack_speed,
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
        if internal.character_type is const.CharacterType.MELEE:
            character_class = prototype.CharacterClass.MELEE
        elif internal.character_type is const.CharacterType.RANGER:
            character_class = prototype.CharacterClass.RANGER
        elif internal.character_type is const.CharacterType.SNIPER:
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
            _spawn_character_type=character_class
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

    # ===============================================================
    # ======= Methods defined below are all callable from AI. =======
    # ===============================================================

    def get_current_time(self):
        return get_model().get_time()

    def get_grid_size(self):
        return const.ARENA_SIZE[0]

    def get_vision_block_size(self) -> float:
        return const.VISION_BLOCK_SIZE

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
        if index < 0 or index >= len(get_model().teams):
            raise IndexError
        team = get_model().teams[index]
        # Should be correct, if model implementation changes this should fail
        if not team.team_id == index:
            log_critical("[API] Team ID mismatch: team.team_id, index")
            raise GameError("Team ID implement has changed.")
        return team.points

    def get_sample_character(self, type_class: prototype.CharacterClass) -> prototype.Character:
        enforce_type('type_class', type_class, prototype.CharacterClass)

        if type_class is prototype.CharacterClass.UNKNOWN:
            raise ValueError
        stats: const.CharacterAttribute
        if type_class is prototype.CharacterClass.MELEE:
            stats = const.MELEE_ATTRIBUTE
        elif type_class is prototype.CharacterClass.SNIPER:
            stats = const.SNIPER_ATTRIBUTE
        elif type_class is prototype.CharacterClass.RANGER:
            stats = const.RANGER_ATTRIBUTE
        else:
            raise ValueError

        extern = prototype.Character(
            _id=-1,
            _type=type_class,
            _position=pg.Vector2(0, 0),
            _speed=stats.speed,
            _attack_range=stats.attack_range,
            _attack_speed=1 / stats.attack_speed,
            _damage=stats.attack_damage,
            _vision=stats.vision,
            _health=stats.max_health,
            _max_health=stats.max_health,
            _team_id=0
        )
        return extern

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
            return prototype.Movement(prototype.MovementStatusClass.UNKNOWN, False)
        with character.moving_lock:
            if character.move_state is CharacterMovingState.STOPPED:
                return prototype.Movement(prototype.MovementStatusClass.STOPPED, False)
            if character.move_state is CharacterMovingState.TO_DIRECTION:
                return prototype.Movement(prototype.MovementStatusClass.TO_DIRECTION, False, self.__transform(character.move_direction.normalize(), is_position=False))
            if character.move_state is CharacterMovingState.TO_POSITION:
                return prototype.Movement(prototype.MovementStatusClass.TO_POSITION, character.is_wandering, self.__transform(character.move_destination, is_position=True))
            raise ValueError

    def refresh_character(self, character: prototype.Character) -> prototype.Character | None:
        enforce_type('character', character, prototype.Character, type(None))

        internal = self.__access_character(character)
        if internal is None or not internal.alive:
            return None
        return self.__register_character(internal)

    def refresh_tower(self, tower: prototype.Tower) -> prototype.Tower:
        enforce_type('tower', tower, prototype.Tower)

        internal = self.__access_tower(tower)
        if not internal.alive:
            raise GameError("Tower died, what?")
        return self.__register_tower(internal)

    def get_visibility(self) -> list[list[int]]:
        vision_grid = np.array(self.__team().vision.bool_mask)

        # Upside down flip
        vision_grid = np.flip(vision_grid, axis=0)
        if self.transform is None:
            self.__build_transform_matrix()

        # Rotate visibility matrix base on transform
        if self.transform[0][0] == 0 and self.transform[0][1] == 1:
            vision_grid = np.rot90(vision_grid)
        elif self.transform[0][0] == -1 and self.transform[0][1] == 0:
            vision_grid = np.rot90(vision_grid, 2)
        elif self.transform[0][0] == 0 and self.transform[0][1] == -1:
            vision_grid = np.rot90(vision_grid, 3)

        # Transform array index into coordinate
        vision_grid = np.flip(vision_grid, axis=0)
        vision_grid = np.rot90(vision_grid)

        # Expand to 250 * 250
        vision_coordinate = [[vision_grid[i // 2][j // 2]
                              for i in range(const.ARENA_SIZE[0])] for j in range(const.ARENA_SIZE[1])]

        return vision_coordinate

    def is_visible(self, position: pg.Vector2) -> bool:
        return self.__team().vision.position_inside_vision(
            self.__transform(position, is_position=True, inverse=True))

    def is_wandering(self, character: prototype.Character) -> bool:
        enforce_type('character', character, prototype.Character)
        return self.__access_character(character).is_wandering

    def get_terrain(self, position: pg.Vector2) -> prototype.MapTerrain:
        w = const.ARENA_SIZE[1]
        if position.x < 0 or position.x > w or position.y < 0 or position.x > w:
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
        for ch in characters:
            enforce_type('element of characters', ch, prototype.Character)

        direction = self.__transform(direction, is_position=False, inverse=True)
        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            with inter.moving_lock:
                inter.set_move_direction(direction)

    def action_move_to(self, characters: Iterable[prototype.Character], destination: pg.Vector2):
        enforce_type('characters', characters, Iterable)
        enforce_type('destination', destination, pg.Vector2)
        for ch in characters:
            enforce_type('element of characters', ch, prototype.Character)

        destination = self.__transform(destination, is_position=True, inverse=True)
        destination_cell = get_model().map.position_to_cell(destination)
        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            old_destination = inter.move_destination
            if old_destination is not None and get_model().map.position_to_cell(inter.move_destination) == destination_cell:
                continue
            with inter.moving_lock:
                inter.set_move_stop()
                path = get_model().map.find_path(inter.position, destination)
                if path is not None and len(path) > 0:
                    inter.set_move_position(path)

    def action_move_clear(self, characters: Iterable[prototype.Character]):
        enforce_type('characters', characters, Iterable)
        for ch in characters:
            enforce_type('element of characters', ch, prototype.Character)

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            with inter.moving_lock:
                inter.set_move_stop()

    def action_attack(self, characters: Iterable[prototype.Character], target: prototype.Character | prototype.Tower):
        enforce_type('characters', characters, Iterable)
        enforce_type('target', target, prototype.Character, prototype.Tower)
        for ch in characters:
            enforce_type('element of characters', ch, prototype.Character)

        target_internal = None
        if isinstance(target, prototype.Character):
            target_internal = self.__access_character(target)
        elif isinstance(target, prototype.Tower):
            target_internal = self.__access_tower(target)

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for internal in internals:
            internal.attack(target_internal)

    def action_cast_ability(self, characters: Iterable[prototype.Character], **kwargs):
        enforce_type('characters', characters, Iterable)
        for ch in characters:
            enforce_type('element of characters', ch, prototype.Character)
        if 'position' in kwargs:
            enforce_type('position', kwargs['position'], pg.Vector2)
            kwargs['position'] = self.__transform(
                kwargs['position'], is_position=True, inverse=True)

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            inter.cast_ability(**kwargs)

    def action_wander(self, characters: Iterable[prototype.Character]):
        enforce_type('characters', characters, Iterable)
        for ch in characters:
            enforce_type('element of characters', ch, prototype.Character)

        internals = [self.__access_character(ch) for ch in characters]
        internals = [inter for inter in internals if self.__is_controllable(inter)]
        for inter in internals:
            with inter.moving_lock:
                inter.set_wandering()

    def change_spawn_type(self, tower: prototype.Tower, spawn_type: prototype.CharacterClass):
        """change the type of character the tower spawns"""
        enforce_type('tower', tower, prototype.Tower)
        enforce_type('spawn_type', spawn_type, prototype.CharacterClass)

        internal_tower = self.__access_tower(tower)
        if not self.__is_controllable(internal_tower):
            return

        internal_tower.update_character_type(Internal.__map_character_type(spawn_type))

    def sort_by_distance(self, characters: Iterable[prototype.Character], target: pg.Vector2) -> list[prototype.Character]:
        enforce_type('characters', characters, Iterable)
        enforce_type('target', target, pg.Vector2)
        for ch in characters:
            enforce_type('element of characters', ch, prototype.Character)

        # We preform no transform at all, as all transform are just translate and rotate.
        # Length is preserved under these operations.
        characters = sorted(characters, key=lambda ch: ch.position.distance_to(target))
        return list(characters)

    def within_attacking_range(self, unit: prototype.Character | prototype.Tower,
                               candidates: list[prototype.Character | prototype.Tower] | None = None) -> list[prototype.Character | prototype.Tower]:
        enforce_type('unit', unit, prototype.Character, prototype.Tower)
        enforce_type('candidates', candidates, list, type(None))
        if candidates is not None:
            for u in candidates:
                enforce_type('element of candidates', u, prototype.Character, prototype.Tower)
        else:
            candidates = self.get_visible_characters() + self.get_visible_towers()

        # We preform no transform at all, as all transform are just translate and rotate.
        # Length is preserved under these operations.
        return [enemy for enemy in candidates
                if (enemy.position - unit.position).length() <= unit.attack_range and enemy.team_id != unit.team_id]

    def within_vulnerable_range(self, unit: prototype.Character | prototype.Tower,
                                candidates: list[prototype.Character | prototype.Tower] | None = None) -> list[prototype.Character | prototype.Tower]:
        enforce_type('unit', unit, prototype.Character, prototype.Tower)
        enforce_type('candidates', candidates, list, type(None))
        if candidates is not None:
            for u in candidates:
                enforce_type('element of candidates', u, prototype.Character, prototype.Tower)
        else:
            candidates = self.get_visible_characters() + self.get_visible_towers()

        # We preform no transform at all, as all transform are just translate and rotate.
        # Length is preserved under these operations.
        return [enemy for enemy in candidates
                if (enemy.position - unit.position).length() <= enemy.attack_range and enemy.team_id != unit.team_id]

    def send_chat(self, msg: str) -> bool:
        enforce_type('msg', msg, str)
        time_stamp = get_model().get_time()
        if time_stamp - self.__last_chat_time_stamp < 1.0:
            return False
        if self.__chat_sent:
            return False
        if len(msg) > 30:
            return False
        # Bad special case, I know. However, that is ensured in the pygame documentation.
        if '\x00' in msg:
            return False
        self.__chat_sent = True
        self.__last_chat_time_stamp = time_stamp
        model.chat.chat.send_comment(team=self.__team(), text=msg)
        return True

    def get_map_name(self) -> str:
        return get_model().map.name


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
        self.ended = False
        self.status_lock = threading.Lock()
        """A lock protecting multithread timer starting and ending."""
        self.for_player_id = None

    def set_timer(self, interval: float, player_id: int, tid: int):
        """Start the timer."""
        with self.status_lock:
            if self.ended:
                return
            if not self.is_windows:
                # pylint: disable=unused-argument
                def handler(sig, frame):
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
        with self.status_lock:
            if not self.started:
                self.ended = True
                return
            try:
                if not self.is_windows:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                else:
                    self.timer.cancel()
            except TimeoutException:
                log_warning("[API] Perhaps some very slightly timeout.")
            self.ended = True


helpers = [Internal(i) for i in range(MAX_TEAMS)]
ai = [None] * len(helpers)


def load_ai(files: list[str]):
    """Load AI modules."""
    for i, file in enumerate(files):
        if file == 'human':
            continue
        spec = importlib.util.find_spec('ai.' + file)
        ai[i] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ai[i])


def threading_ai(team_id: int, helper: Internal, timer: Timer):
    """Threading AI helper function."""
    try:
        if ai[team_id] is not None:
            ai[team_id].every_tick(helper)
    except TimeoutException:
        log_critical(f"[API] AI of team {team_id} timed out!")
    # pylint: disable=broad-exception-caught
    except Exception:
        log_critical(f"Caught exception in AI of team {team_id}:\n{traceback.format_exc()}")
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
