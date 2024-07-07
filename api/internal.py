from __future__ import annotations

import importlib
import os
import signal
import threading
import traceback
import warnings
from typing import Iterable

import pygame as pg

import api.prototype as prototype
import model
import model.character
import model.character.melee
import model.character.ranger
import model.character.sniper
from const import FPS, MAX_TEAMS
from instances_manager import get_model


class GameError(Exception):
    def __init__(self, message):
        super().__init__("The game broke. This is not your fault. Please contact us so we can fix it." + message)


class Internal(prototype.API):
    def __init__(self, team_id: int):
        self.team_id = team_id
        self.__character_map = {}
        self.__tower_map = {}
        self.__reverse_character_map = {}
        self.__reverse_tower_map = {}

    def clear_map(self):
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

    def __register_character(self, internal: model.Character) -> prototype.Character:
        """
        Register a `model.Character` to `api.Character`.
        Therefore, API can only manipulate a character using the given interface 
        while we still know the original `model.Character`.
        """

        if internal.id not in self.__character_map:
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
            self.__character_map[internal.id] = extern
            self.__reverse_character_map[id(extern)] = internal
        return self.__character_map[internal.id]

    def __register_tower(self, internal: model.Tower) -> prototype.Tower:
        """
        Register a `model.Tower` to `api.Tower` like above.
        """
        if internal.id not in self.tower_map:
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
                _team_id=Internal.__cast_id(internal.team.team_id)
            )
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

    def __team(self):
        return get_model().teams[self.team_id]

    def get_time(self):
        return get_model().get_time()

    def get_characters(self) -> list[prototype.Character]:
        return [self.__register_character(character)
                for character in self.__team().character_list]

    def get_towers(self) -> list[prototype.Tower]:
        return [self.__register_tower(tower)
                for tower in self.__team().towers]

    def get_team_id(self) -> int:
        return Internal.__cast_id(self.__team().team_id)

    def get_score(self, index=None) -> int:
        if index == None:
            index = self.team_id
        if not isinstance(index, int):
            raise TypeError("Team index must be type int or None.")
        if index < 0 or index >= MAX_TEAMS:
            raise IndexError
        team = get_model().teams[index]
        # Should be correct, if model implementation changes this should fail
        if not team.team_id == index:
            print(team.team_id, index)
            raise GameError("Team ID implement has changed.")
        return team.points

    def action_move_along(self, characters: Iterable[prototype.Character], direction: pg.Vector2):
        if not isinstance(characters, Iterable):
            raise TypeError("Character is not iterable.")
        for ch in characters:
            if not isinstance(ch, prototype.Character):
                raise TypeError("List contains non-character.")
            internal = self.__access_character(ch)
            if internal == None:
                continue
            # internal.move_direction = direction
            raise NotImplementedError

    def change_spawn_type(self, tower: model.Tower, spawn_type: prototype.CharacterClass):
        pass


class Timer():
    def __init__(self):
        if os.name == 'nt':
            self.is_windows = True
        elif os.name == 'posix':
            self.is_windows = False
        else:  # os.name == 'java' or unknown
            raise OSError

        if not self.is_windows:
            def handler(sig, frame):
                raise TimeoutError()

            signal.signal(signal.SIGALRM, handler)
        self.timer = None
        self.for_player_id = None

    def set_timer(self, interval: float, player_id: int):
        if not self.is_windows:
            signal.setitimer(signal.ITIMER_REAL, interval)
        else:
            def timeout_alarm(player_id: int):
                print(f"The AI of player {player_id} time out!")

            self.timer = threading.Timer(interval=interval, function=timeout_alarm,
                                         args=[player_id])
            self.timer.start()

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
timer = Timer()


def load_ai(files: list[str]):
    for i, file in enumerate(files):
        if file == 'human':
            continue
        ai[i] = importlib.import_module('ai.' + file)


def call_ai(team_id):
    if ai[team_id] == None:
        return

    try:
        timer.set_timer(1 / (4 * FPS), team_id)
        ai[team_id].every_tick(helpers[team_id])
    except Exception as e:
        print(f"Caught exception in AI of team {team_id}:")
        print(traceback.format_exc())
        return
    finally:
        timer.cancel_timer()
