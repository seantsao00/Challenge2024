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
        self.id = _id
        """角色獨一的編號。編號可以用來識別不同時間的角色是否是相同的一個實體。"""
        self.type = _type
        """角色的兵種。"""
        self.position = _position
        """角色的位置。"""
        self.speed = _speed
        """角色的最大移動速度。"""
        self.attack_range = _attack_range
        """角色的最大攻擊範圍。"""
        self.damage = _damage
        """角色的傷害。"""
        self.vision = _vision
        """角色的視野半徑。"""
        self.health = _health
        """角色的當下血量。"""
        self.max_health = _max_health
        """角色的最大血量。"""
        self.team_id = _team_id
        """角色所屬的隊伍編號。"""


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
        self.id = _id
        """建築物獨一的編號。編號可以用來識別不同時間的建築物是否是相同的一個實體。"""
        self.period = _period
        """建築物產生角色的所需時間。"""
        self.position = _position
        """建築物所在的位置。"""
        self.is_fountain = _is_fountain
        """建築物是否是溫泉（每個隊伍一開始的建築）。"""
        self.spwan_character_type = _spwan_character_type
        """建築物即將生成的角色種類。"""
        self.attack_range = _attack_range
        """建築物的攻擊範圍。"""
        self.damage = _damage
        """建築物的傷害。"""
        self.vision = _vision
        """建築物的視野範圍。"""
        self.health = _health
        """建築物的血量。"""
        self.max_health = _max_health
        """建築物的最大血量。"""
        self.team_id = _team_id
        """建築物所屬的隊伍編號。"""


class API:
    def get_time(self):
        """回傳現在的遊戲時間。"""
        pass

    def get_characters(self) -> list[Character]:
        """回傳隊伍擁有的所有角色。"""
        pass

    def get_towers(self) -> list[Tower]:
        """回傳隊伍擁有的所有建築。"""
        pass

    def get_team_id(self) -> int:
        """Return current team's `id`."""

    def get_score(self, index=None) -> int:
        """Return the score of team `index`. If `index` is 0, return the current team's score."""
        pass

    def look_characters(self) -> list[Character]:
        """回傳該隊伍視野可及的所有角色。"""
        pass

    def look_towers(self) -> list[Tower]:
        """回傳該隊伍視野可及的所有建築。"""
        pass

    def look_grid(self) -> list[list[int]]:
        """Return a grid of current vision."""
        pass

    def action_move_to(self, characters: Iterable[Character], destination: pg.Vector2):
        """
        讓所有角色移動到目的地。
        此功能會覆蓋先前的指令。
        """
        pass

    def action_attack(self, characters: Iterable[Character], target: Character | Tower):
        """
        讓所有角色攻擊目標，目標需要在其攻擊範圍內。
        此功能會覆蓋先前的指令。
        """
        pass

    def action_move_along(self, characters: Iterable[Character], direction: pg.Vector2):
        """
        讓所有角色朝 direction 的方向移動，直到被指派新的指令，可能會撞到牆或障礙物。
        此功能會覆蓋先前的指令。
        """
        pass

    def action_cast_spell(self, characters: Iterable[Character], target: pg.Vector2 = None):
        """
        Make all characters in the list cast their spell. If the cooldown isn't ready, nothing happens for the character. Target will be used for ranged spell. For separate target call this function multiple times.
        """
        pass

    def action_clear(self, characters: Iterable[Character]):
        """
        清除所有角色先前的指令 (讓所有角色靜止不動)。
        """
        pass

    def change_spawn_type(self, tower: Tower, spawn_type: CharacterClass):
        """改變特定塔生成的兵種。"""
        pass

    def sort_by_distance(self, characters: Iterable[Character], target: pg.Vector2):
        """將各角色依據其與目標的距離排序，若距離一樣則隨意排序。"""
        pass
