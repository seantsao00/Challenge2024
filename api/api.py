"""
This file ONLY defines prototype. No actual thing is done in this file.
The document of the API is at https://hackmd.io/@seantsao00/challenge_2024_api/edit.
"""

from dataclasses import dataclass
from enum import IntEnum, auto

import pygame as pg


class CharacterClass(IntEnum):
    """角色種類。`melee`、`lookout`、`ranged` 分別代表近戰、視野以及遠程兵。"""
    melee = auto()
    lookout = auto()
    ranged = auto()
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


@dataclass
class CharacterAction():
    direction: pg.Vector2
    attack_target_id: int
    spell: bool
    spell_target: pg.Vector2 = None


@dataclass
class Action():
    towers_actions: list[tuple[int, CharacterClass]]
    characters_actions: list[tuple[int, CharacterAction]]


class AI:
    def make_move(self) -> Action:
        pass


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

    def get_score(self, index=0) -> int:
        """Return the score of team `index`. If `index` is 0, return the current team's score."""
        pass

    def look_characters(self) -> list[Character]:
        """Return the list of charactervisible from the team."""
        pass

    def look_towers(self) -> list[Tower]:
        """Return the list of tower visible from the team."""
        pass

    def look_grid(self) -> list[Tower]:
        """Return a grid of current vision."""
        pass

    def action_move_to(self, characters: list[Character], destination: tuple[float, float]):
        """
        Make all characters in the list move to the destination, using internal A* algorithm.
        This function override previous action.
        """
        pass

    def action_attack(self, characters: list[Character], target: Character | Tower):
        """
        Make all characters in the list attack the target. Target has to be in their attack radii.
        This function override previous action.
        """
        pass

    def action_move_along(self, characters: list[Character], direction: tuple[float, float]):
        """
        Make all characters in the list move along the direction. May bump into the wall or border.
        This function override previous action.
        """
        pass

    def action_clear(self, characters: list[Character]):
        """
        Clear previous assigned action of all characters in the list. (They will stand still)
        """
        pass

    def change_spawn_type(self, tower: Tower, spawn_type: CharacterClass):
        """Change the spawning character type of a tower."""
        pass

    def sort_by_distance(self, characters: list[Character], target: tuple[float, float]):
        """Sort the whole character list according to the distance from target. Tie breaked arbitrarily."""
        pass
