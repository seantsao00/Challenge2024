"""
This file ONLY defines prototype. No actual thing is done in this file.
The document of the API is at https://hackmd.io/@seantsao00/challenge_2024_api/edit.
"""

from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Iterable

import pygame as pg


class CharacterClass(IntEnum):
    """角色種類。`melee`、`lookout`、`ranged` 分別代表近戰、視野以及遠程兵。"""
    melee = auto()
    sniper = auto()
    ranger = auto()
    unknown = auto()
    pass


class Character:
    """角色"""

    def __init__(self,
                 _id: int,
                 _type: CharacterClass,
                 _position: pg.Vector2,
                 _speed: float,
                 _attack_range: float,
                 _damage: float,
                 _vision: float,
                 _health: float,
                 _max_health: float,
                 _team_id: int):
        self.__id = _id
        self.__type = _type
        self.__position = _position
        self.__speed = _speed
        self.__attack_range = _attack_range
        self.__damage = _damage
        self.__vision = _vision
        self.__health = _health
        self.__max_health = _max_health
        self.__team_id = _team_id

    @property
    def id(self) -> int:
        """回傳獨一的編號。編號可以用來識別不同時間的角色是否是相同的一個實體。"""
        return self.__id

    @property
    def type(self) -> CharacterClass:
        """回傳角色的兵種。"""
        return self.__type

    # TODO: add other properties


class Tower:
    """Tower used for maniplutaing (prevents direct access to actual tower)"""

    def __init__(self,
                 _id: int,
                 _position: pg.Vector2,
                 _period: float,
                 _is_fountain: bool,
                 _spwan_character_type: CharacterClass,
                 _attack_range: float,
                 _damage: float,
                 _vision: float,
                 _health: float,
                 _max_health: float,
                 _team_id: int):
        self.__id = _id
        self.__period = _period
        self.__position = _position
        self.__is_fountain = _is_fountain
        self.__spwan_character_type = _spwan_character_type
        self.__attack_range = _attack_range
        self.__damage = _damage
        self.__vision = _vision
        self.__health = _health
        self.__max_health = _max_health
        self.__team_id = _team_id

    # TODO: add other properties


class API:
    def get_time(self):
        """Return the current in-game time."""
        pass

    def get_characters(self) -> list[Character]:
        """Return the list of character owned by the team."""
        pass

    def get_towers(self) -> list[Tower]:
        """Return the list of tower owned by the team."""
        pass

    def get_team_id(self) -> int:
        """Return current team's `id`."""

    def get_score(self, index=None) -> int:
        """Return the score of team `index`. If `index` is 0, return the current team's score."""
        pass

    def look_characters(self) -> list[Character]:
        """Return the list of charactervisible from the team."""
        pass

    def look_towers(self) -> list[Tower]:
        """Return the list of tower visible from the team."""
        pass

    def look_grid(self) -> list[list[int]]:
        """Return a grid of current vision."""
        pass

    def action_move_to(self, characters: Iterable[Character], destination: pg.Vector2):
        """
        Make all characters in the list move to the destination, using internal A* algorithm.
        This function override previous action.
        """
        pass

    def action_attack(self, characters: Iterable[Character], target: Character | Tower):
        """
        Make all characters in the list attack the target. Target has to be in their attack radii.
        This function override previous action.
        """
        pass

    def action_move_along(self, characters: Iterable[Character], direction: pg.Vector2):
        """
        Make all characters in the list move along the direction. May bump into the wall or border.
        This function override previous action.
        """
        pass

    def action_cast_spell(self, characters: Iterable[Character], target: pg.Vector2 = None):
        """
        Make all characters in the list cast their spell. If the cooldown isn't ready, nothing happens for the character. Target will be used for ranged spell. For separate target call this function multiple times.
        """
        pass

    def action_clear(self, characters: Iterable[Character]):
        """
        Clear previous assigned action of all characters in the list. (They will stand still)
        """
        pass

    def change_spawn_type(self, tower: Tower, spawn_type: CharacterClass):
        """改變特定塔生成的兵種"""
        pass

    def sort_by_distance(self, characters: Iterable[Character], target: pg.Vector2):
        """Sort the whole character list according to the distance from target. Tie breaked arbitrarily."""
        pass
