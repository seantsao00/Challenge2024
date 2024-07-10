"""
This file ONLY defines prototype. No actual thing is done in this file.
The document of the API is at https://hackmd.io/@seantsao00/challenge_2024_api/edit.
"""

from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import Iterable

import pygame as pg


class CharacterClass(IntEnum):
    """角色種類。"""
    melee = auto()
    sniper = auto()
    ranger = auto()
    unknown = auto()
    pass


class Character:
    """角色。"""

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
    """建築物。"""

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
    def get_current_time(self):
        """回傳當下的遊戲進行時間，單位為秒。"""
        pass

    def get_owned_characters(self) -> list[Character]:
        """回傳自己隊伍所擁有的角色。"""
        pass

    def get_owned_towers(self) -> list[Tower]:
        """回傳自己隊伍所擁有的建築。"""
        pass

    def get_team_id(self) -> int:
        """回傳自己隊伍的編號（`id`）。"""
        pass

    def get_score_of_team(self, index=None) -> int:
        """
        回傳指定隊伍的編號，回傳該隊伍的分數。如果隊伍沒有指定則回傳自己隊伍的分數。
        @index: 隊伍的編號或者是 `None`（代表自己的小隊）
        """
        pass

    def get_visible_characters(self) -> list[Character]:
        """回傳在自己視野範圍當中的角色，請注意這個函數也會回傳自己的角色。"""
        pass

    def get_visible_towers(self) -> list[Tower]:
        """回傳在自己視野範圍當中的建築，請注意這個函數也會回傳自己的建築。"""
        pass

    def get_visibility(self) -> list[list[int]]:
        """Deprecated. use `is_visible` instead."""
        pass

    def is_visible(self, position: pg.Vector2) -> bool:
        """回傳某個位置是否在視野範圍內。如果位置在地圖之外，永遠回傳 `False`。
        @position: 要檢查的位置。"""
        pass

    def action_move_along(self, characters: Iterable[Character], direction: pg.Vector2):
        """
        將所有列表中的角色設定為沿著某個向量移動。
        @characters: 角色的 `list` 或者 `tuple`（任意 `Iterable`）。
        @direction: 移動的向量。
        """
        pass

    def action_move_to(self, characters: Iterable[Character], destination: pg.Vector2):
        """
        將所有列表中的角色設定為朝著某個目的地移動。如果目標不在視野範圍內或者不是可以行走的位置則不會生效。
        這個函數會使用內建的巡路，可能會耗費大量時間，使用時請注意耗用時間。
        @characters: 角色的 `list` 或者 `tuple`（任意 `Iterable`）。
        @destination: 移動的目的地。
        """
        pass

    def action_move_clear(self, characters: Iterable[Character]):
        """
        將所有列表中的角色設定為不移動。
        @characters: 角色的 `list` 或者 `tuple`（任意 `Iterable`）。
        """
        pass

    def action_attack(self, characters: Iterable[Character], target: Character | Tower):
        """
        將所有列表中的角色設定為攻擊某個目標。如果是友方傷害、攻擊冷卻還未結束或者是不在攻擊範圍內則不會攻擊。
        @characters: 角色的 `list` 或者 `tuple`（任意 `Iterable`）。
        @destination: 移動的目的地。
        """
        pass

    def action_cast_spell(self, characters: Iterable[Character], target: pg.Vector2 = None):
        """
        將所有列表中的角色設定為使用技能。如果是技能冷卻還未結束或者是不在攻擊範圍內則不會使用。
        @characters: 角色的 `list` 或者 `tuple`（任意 `Iterable`）。
        """
        pass

    def action_wander(self, characters: Iterable[Character]):
        """
        將所有列表內的角色設定為遊蕩。
        @characters: 角色的 `list` 或者 `tuple`（任意 `Iterable`）。
        """
        pass

    def change_spawn_type(self, tower: Tower, spawn_type: CharacterClass):
        """
        改變指定塔所生成的兵種。
        @tower: 指定的建築。
        @spawn_type: 指定的兵種。
        """
        pass

    def sort_by_distance(self, characters: Iterable[Character], target: pg.Vector2):
        """將各角色依據其與目標的距離排序，若距離一樣則隨意排序。"""
        pass
