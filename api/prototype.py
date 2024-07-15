"""
This file ONLY defines prototype. No actual thing is done in this file.
"""

from abc import abstractmethod
from enum import IntEnum, auto
from typing import Iterable

import pygame as pg


class CharacterClass(IntEnum):
    """士兵種類。"""

    MELEE = auto()
    SNIPER = auto()
    RANGER = auto()
    UNKNOWN = auto()


class Character:
    """士兵。"""

    def __init__(self,
                 _id: int,
                 _type: CharacterClass,
                 _position: pg.Vector2,
                 _speed: float,
                 _attack_range: float,
                 _attack_speed: float,
                 _damage: float,
                 _vision: float,
                 _health: float,
                 _max_health: float,
                 _team_id: int):
        self.id = _id
        """士兵唯一的編號。編號可以在不同時間，用來識別某個士兵是否為相同的一個實體。"""

        self.type = _type
        """士兵的兵種。"""

        self.position = _position
        """士兵的位置。"""

        self.speed = _speed
        """士兵的最大移動速度。"""

        self.attack_range = _attack_range
        """士兵的最大攻擊範圍。"""

        self.attack_speed = _attack_speed
        """士兵的攻擊時間間隔。"""

        self.damage = _damage
        """士兵的傷害。"""

        self.vision = _vision
        """士兵的視野半徑。"""

        self.health = _health
        """士兵的當下血量。"""

        self.max_health = _max_health
        """士兵的最大血量。"""

        self.team_id = _team_id
        """士兵所屬的隊伍編號，編號為 1 至 4 的正整數。"""


class Tower:
    """塔。"""

    def __init__(self,
                 _id: int,
                 _position: pg.Vector2,
                 _period: float,
                 _is_fountain: bool,
                 _spawn_character_type: CharacterClass,
                 _attack_range: float,
                 _damage: float,
                 _vision: float,
                 _health: float,
                 _max_health: float,
                 _team_id: int):
        self.id = _id
        """塔唯一的編號。編號可以在不同時間，用來識別某個塔是否為相同的一個實體。"""

        self.period = _period
        """塔產生一隻士兵的所需時間。"""

        self.position = _position
        """塔所在的位置。"""

        self.is_fountain = _is_fountain
        """塔是否是主堡（每個隊伍一開始的塔）。"""

        self.spawn_character_type = _spawn_character_type
        """塔即將生成的士兵種類。"""

        self.attack_range = _attack_range
        """塔的攻擊範圍。"""

        self.damage = _damage
        """塔的傷害。"""

        self.vision = _vision
        """塔的視野範圍。"""

        self.health = _health
        """塔的當下血量。"""

        self.max_health = _max_health
        """塔的最大血量。"""

        self.team_id = _team_id
        """塔所屬的隊伍編號，編號為 1 至 4 的正整數，或者 0 代表中立。"""


class MapTerrain(IntEnum):
    """地圖地形。"""

    OUT_OF_BOUNDS = auto()
    """界外。"""

    ROAD = auto()
    """道路。走路的速度是正常的。"""

    OFFROAD = auto()
    """非道路，走路會減速。"""

    OBSTACLE = auto()
    """障礙物，無法通過。"""


class MovementStatusClass(IntEnum):
    """士兵移動的狀態。 """

    STOPPED = auto()
    """士兵目前停止。 """

    TO_DIRECTION = auto()
    """士兵目前正朝某個方向前進。 """

    TO_POSITION = auto()
    """士兵目前朝著某個點為目的地前進。 """

    UNKNOWN = auto()
    """無法得知的狀況，例如無法得知敵隊士兵的移動狀況。"""


class Movement:
    def __init__(self,
                 _status: MovementStatusClass,
                 _is_wandering: bool,
                 _vector: pg.Vector2 | None = None):
        self.status = _status
        """士兵的移動狀態。 """

        self.is_wandering = _is_wandering
        """
        士兵是否在遊蕩狀態。
        一個士兵一旦被設為遊蕩，則除非該士兵無法再遊蕩，或被指定其他移動方式（如：`action_move_along`, `action_move_to`, `action_move_clear`）才會又變為 `False`。
        """

        self.vector = _vector
        """
        當停止時，為 `None`。
        當朝某個方向時，為朝著的方向，且為一個正規化後（長度為 1）的向量。
        當朝著某個點時，為該點的座標。
        """


class API:
    """與遊戲互動的方法。傳入 AI 的方法是讓其作為 `every_tick` 的第一個引數。"""

    # ==== 場地資訊獲取 ====

    @abstractmethod
    def get_current_time(self) -> float:
        """回傳當下的遊戲進行時間，單位為秒。"""
        raise NotImplementedError

    @abstractmethod
    def get_grid_size(self) -> float:
        """回傳遊戲網格的長寬，由於遊戲網格是正方形的，長寬都使用這個函數。"""
        raise NotImplementedError

    @abstractmethod
    def get_team_id(self) -> int:
        """回傳自己隊伍的編號（`id`）。"""
        raise NotImplementedError

    @abstractmethod
    def get_score_of_team(self, index=None) -> int:
        """
        回傳指定隊伍的分數。如果沒有指定隊伍，則回傳自己隊伍的分數。  
        @index: 隊伍的編號或者是 `None`（代表自己的小隊）
        """
        raise NotImplementedError

    @abstractmethod
    def get_visibility(self) -> list[list[int]]:
        """
        回傳目前所有的視野狀態。回傳值是一個二維的表格，長寬皆為 `get_grid_size()` 的回傳值。
        """
        raise NotImplementedError

    @abstractmethod
    def is_visible(self, position: pg.Vector2) -> bool:
        """回傳某個位置是否在視野範圍內。如果位置在地圖之外，永遠回傳 `False`。  
        @position: 要檢查的位置。"""
        raise NotImplementedError

    @abstractmethod
    def get_terrain(self, position: pg.Vector2) -> MapTerrain:
        """回傳某個位置的地形，不需在視野範圍內就能呼叫。  
        如果位置在地圖之外，回傳 `OUT_OF_BOUNDS`。
        @position: 要檢查的位置。"""

    @abstractmethod
    def get_map_name(self) -> str:
        """回傳當前地圖的名稱"""

    # ==== 士兵、塔資訊獲取 ====

    @abstractmethod
    def get_sample_character(self, type_class: CharacterClass) -> Character:
        """
        給定士兵種類，回傳一個「無法控制」的士兵，這個士兵會擁有給定士兵種類的數值（例如血量），
        可以用來獲取特定種類士兵的數據。這個士兵的`id` 為 -1、座標為原點、而隊伍 `team_id` 為 0。

        @type_class: 士兵種類，不能是 `UNKNOWN`。

        ## 使用範例：

        輸出近戰士兵的血量。

        >>> interface: api.prototype.API
        >>> sample_melee = interface.get_sample_character(api.prototype.CharacterClass.MELEE)
        >>> print(sample_melee.health)
        """
        raise NotImplementedError

    @abstractmethod
    def get_owned_characters(self) -> list[Character]:
        """
        回傳自己隊伍所擁有的士兵。
        預設回傳按照士兵的 `id` 排序。
        """
        raise NotImplementedError

    @abstractmethod
    def get_owned_towers(self) -> list[Tower]:
        """
        回傳自己隊伍所擁有的塔。
        預設回傳按照塔的 `id` 排序。
        """
        raise NotImplementedError

    @abstractmethod
    def get_visible_characters(self) -> list[Character]:
        """
        回傳在自己視野範圍當中的士兵，請注意這個函數也會回傳自己的士兵。
        預設回傳按照士兵的 `id` 排序。
        """
        raise NotImplementedError

    @abstractmethod
    def get_visible_towers(self) -> list[Tower]:
        """
        回傳在自己視野範圍當中的塔，請注意這個函數也會回傳自己的塔。
        預設回傳按照塔的 `id` 排序。
        """
        raise NotImplementedError

    @abstractmethod
    def refresh_character(self, character: Character) -> Character | None:
        """
        更新一個士兵的數值。如果士兵死亡則回傳 None。  
        @character: 目標的士兵。
        """

    @abstractmethod
    def refresh_tower(self, tower: Tower) -> Tower:
        """
        更新一個塔的數值。  
        @tower: 目標的塔。
        """

    @abstractmethod
    def get_movement(self, character: Character) -> Movement:
        """
        回傳目標士兵目前的移動狀況。士兵必須是自己隊伍的且當下活著，否則會回傳 `UNKNOWN`。  
        @character: 目標的士兵。
        """

    # ==== 士兵操作相關 ====

    @abstractmethod
    def action_move_along(self, characters: Iterable[Character], direction: pg.Vector2) -> None:
        """
        將所有列表中的士兵，設定為沿著某個向量移動。  
        @characters: 士兵的 `list` 或者 `tuple`（任意 `Iterable`）。  
        @direction: 移動的向量。
        """
        raise NotImplementedError

    @abstractmethod
    def action_move_to(self, characters: Iterable[Character], destination: pg.Vector2) -> None:
        """
        將所有列表中的士兵，設定為朝著某個目的地移動。如果目的地不是可行走的位置則不會生效。
        這個函數會使用內建的尋路，可能會耗費大量時間，使用時請注意。  
        @characters: 士兵的 `list` 或者 `tuple`（任意 `Iterable`）。  
        @destination: 移動的目的地。
        """
        raise NotImplementedError

    @abstractmethod
    def action_wander(self, characters: Iterable[Character]) -> None:
        """
        將所有列表內的士兵設定為遊蕩狀態。
        @characters: 士兵的 `list` 或者 `tuple`（任意 `Iterable`）。
        """
        raise NotImplementedError

    @abstractmethod
    def action_move_clear(self, characters: Iterable[Character]) -> None:
        """
        將所有列表中的士兵設定為不移動。  
        @characters: 士兵的 `list` 或者 `tuple`（任意 `Iterable`）。
        """
        raise NotImplementedError

    @abstractmethod
    def action_attack(self, characters: Iterable[Character], target: Character | Tower) -> None:
        """
        將所有列表中的士兵設定為攻擊某個目標。如果是己方傷害、攻擊冷卻還未結束或者是不在攻擊範圍內則不會攻擊。  
        @characters: 士兵的 `list` 或者 `tuple`（任意 `Iterable`）。  
        @destination: 移動的目的地。
        """
        raise NotImplementedError

    @abstractmethod
    def action_cast_ability(self, characters: Iterable[Character], **kwargs) -> None:
        """
        將所有列表中的士兵設定為使用技能。如果是技能冷卻還未結束或者是不在攻擊範圍內則不會使用。  
        @characters: 士兵的 `list` 或者 `tuple`（任意 `Iterable`）。  
        @kwargs: 所有技能參數的聯集，以下是可用列表：
         - `position`: `pg.Vector2`，遠程士兵使用技能的位置   

        ### 使用範例

        使用所有士兵的技能，不過遠程會在自己的位置釋放：

        >>> interface: api.prototype.API
        >>> interface.action_cast_ability(interface.get_owned_character())

        使用所有遠程的技能，在自己的主堡釋放：

        >>> interface: api.prototype.API
        >>> fountain = interface.get_owned_towers()[0]
        >>> interface.action_cast_ability(
        ...     [character for character in interface.get_owned_characters()
        ...     if character.type is api.prototype.CharacterClass.RANGER],
        ...     position=fountain.position)

        如果 `kwargs` 給定的參數型別不符會收到 TypeError。
        """
        raise NotImplementedError

    # ==== 塔操作 ====

    @abstractmethod
    def change_spawn_type(self, tower: Tower, spawn_type: CharacterClass) -> None:
        """
        改變指定塔所生成的兵種。  
        @tower: 指定的塔。  
        @spawn_type: 指定的兵種。
        """
        raise NotImplementedError

    # ==== 輔助函數 ====

    @abstractmethod
    def sort_by_distance(self, characters: Iterable[Character], target: pg.Vector2) -> list[Character]:
        """
        將各士兵依據其與目標的距離排序，若距離一樣則隨意排序。  
        @characters: 指定的士兵列表。  
        @target: 指定的目標座標。
        """
        raise NotImplementedError

    @abstractmethod
    def within_attacking_range(self, unit: Character | Tower,
                               candidates: list[Character | Tower] | None = None) -> list[Character | Tower]:
        """
        給定一個攻擊者以及潛在目標，回傳在潛在目標的列表中，攻擊者可以攻擊到的所有目標。如果潛在目標為 None 則預設其為所有看的到的實體。只會回傳敵隊實體。
        這個函數只是普通暴力的包裝。
        @unit: 指定的攻擊者。  
        @candidates: 潛在目標（要考慮的所有實體）。
        """
        raise NotImplementedError

    @abstractmethod
    def within_vulnerable_range(self, unit: Character | Tower,
                                candidates: list[Character | Tower] | None = None) -> list[Character | Tower]:
        """
        給定一個實體以及潛在目標，回傳可能被攻擊的所有目標。如果潛在目標為 None 則預設為所有看的到的實體。只會回傳敵隊實體。
        這個函數只是普通暴力的包裝。
        @unit: 指定的被攻擊者。  
        @candidates: 要考慮的所有實體。
        """
        raise NotImplementedError

    # ==== 聊天室 ====

    @abstractmethod
    def send_chat(self, msg: str) -> bool:
        """
        傳送聊天室訊息，每個 `every_tick` 的呼叫當中只能傳送一次。回傳值為傳送成功或失敗。每一次訊息成功傳送後要等待一秒才能傳送下一則訊息。
        @msg: 要傳送的訊息，長度如果超過 30 後面的文字會被忽略、不得包含 NULL 字元。部分字元可能會因為字體無法顯示。
        """
