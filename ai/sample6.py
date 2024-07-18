"""

"""

import math
import random

import pygame as pg

from api.prototype import *


class StageClass(IntEnum):
    """
    定義不同階段的constant。
    你可以加入不同的stage，來增進你的策略！
    """
    START = auto()
    """開始階段"""

    EXPLORE = auto()
    """探索階段"""

    ATTACK_TOWER = auto()
    """攻擊塔階段"""

    DEFENCE_TOWER = auto()
    """防禦塔階段"""

    # ATTACK_ENEMY = auto()
    # """攻擊敵人階段"""

class AiInfo():
    """所有有用到的資料儲存"""
    def __init__(self) -> None:
        self.team_id: int
        self.fountain: Tower | None = None

        self.stage: StageClass = StageClass.START

        self.target_tower: Tower | None = None
        # self.target_enemy: Character | None = None
        self.defend_tower: Tower | None = None


def update(api: API):
    """
    在每一個tick更新會用到的變數。
    因為每個tict所拿到的實例都不同，如果我們要取得同一個id的實例，需要更新。
    """
    if info.fountain is not None:
        info.fountain = api.refresh_tower(info.fountain)
    if info.defend_tower is not None:
        info.defend_tower = api.refresh_tower(info.defend_tower)
    if info.target_tower is not None:
        info.target_tower = api.refresh_tower(info.target_tower)
    # if info.target_enemy is not None:
    #     info.target_enemy = api.refresh_character(info.target_enemy)

    # 開技能
    api.action_cast_ability(api.get_owned_characters())

def change_spawn_by_posibility(api: API, towers: list[Tower], melee_p: float, ranger_p: float, siniper_p: float):
    """
    機率性改變塔生成的兵種
    """
    assert((melee_p + ranger_p + siniper_p == 1))
    spawn_type = random.choices([CharacterClass.MELEE, CharacterClass.RANGER, CharacterClass.SNIPER], \
                                [melee_p, ranger_p, siniper_p])[0]
    for tower in towers:
        api.change_spawn_type(tower, spawn_type)

def stage_start(api: API):
    """
    最開始的階段，會對某些變數初始化。
    """
    info.team_id = api.get_team_id()
    info.fountain = api.get_owned_towers()[0]

def stage_explore(api: API):
    """
    探索地圖階段，會讓所有的士兵在地圖上亂走。
    """
    # 讓主堡生成
    change_spawn_by_posibility(api, api.get_owned_towers(), 1, 0, 0)
    for character in api.get_owned_characters():
        api.action_wander(character)

    # 如果找到不屬於自己的塔，就存起來
    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]
    if len(others_towers) != 0:
        info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]

def stage_attack_tower(api: API):
    """
    攻擊塔階段，會讓所有的士兵都去往某個塔走，進行攻擊。
    """
    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.6, 0.4, 0)

    # 攻擊塔
    api.action_move_to(api.get_owned_characters(), info.target_tower.position)
    api.action_attack(api.get_owned_characters(), info.target_tower)

def stage_defend_tower(api: API):
    """
    防禦塔階段，會讓所有的士兵都往某個塔走，進行攻擊。
    """
    # 改變塔生成的兵種，讓我們更容易把塔守好！
    for tower in api.get_owned_towers():
        if tower.is_fountain:
            change_spawn_by_posibility(api, [tower], 1, 0, 0)
        else:
            change_spawn_by_posibility(api, [tower], 0.4, 0, 0.6)

    # move(api, api.get_owned_characters(), info.defend_tower.position)
    # 往我們要守的塔移動！
    api.action_move_to(api.get_owned_characters(), info.defend_tower.position)

# def stage_attack_enemy(api: API):
#     """
#     攻擊其他人的階段，會讓所有的士兵都往某個敵對士兵走。
#     """
#     # 如果已經有要攻擊的士兵了
#     pass


info = AiInfo()

def every_tick(api: API):
    """
    一定要被實作的 function ，會定期被遊戲 call
    在使用 VS Code 寫 code 的時候可以把滑鼠移到變數、函數上方，看它們的詳細解說。
    在使用 VS Code 寫 code 的時候可以按住 Ctrl 再用滑鼠點擊變數、函數，來跳轉到與它們相關的地方。
    在測試的時候可以只放一隻 ai 、在執行時一次加很多 arguments (如 -qrp)。
    """

    update(api)

    if info.stage == StageClass.START:
        stage_start(api)
        print(f"team {info.team_id} is on stage START")
        info.stage = StageClass.EXPLORE

    if info.stage == StageClass.EXPLORE:
        print(f"team {info.team_id} is on stage EXPLORE")
        stage_explore(api)

        # 找到塔後，向塔攻擊
        if info.target_tower is not None:
            info.stage = StageClass.ATTACK_TOWER

    elif info.stage == StageClass.ATTACK_TOWER:
        print(f"team {info.team_id} is on stage ATTACK_TOWER")
        stage_attack_tower(api)

        # 打下塔了，開始守塔
        if info.target_tower.team_id == info.team_id:
            info.defend_tower = info.target_tower
            info.target_tower = None
            info.stage = StageClass.DEFENCE_TOWER

    elif info.stage == StageClass.DEFENCE_TOWER:
        print(f"team {info.team_id} is on stage DEFENCE_TOWER")
        stage_defend_tower(api)

        # 塔被人打下了，打回來！
        if info.defend_tower is not None and info.defend_tower.team_id != api.get_team_id():
            info.target_tower = info.defend_tower
            info.stage = StageClass.ATTACK_TOWER
        # if ...你認為可以開始打人的時候:
        #     info.stage = StageClass.ATTACK_ENEMY

    # elif info.stage == StageClass.ATTACK_ENEMY:
    #     print(f"team {info.team_id} is on stage ATTACK_ENEMY")
        # stage_attack_enemy(api)
    else:
        print("wrong stage")
        info.stage = StageClass.EXPLORE

    # 設定所有人都會攻擊某一個目標，邊走邊攻擊！
    for character in api.get_owned_characters():
        enemy = api.within_attacking_range(character)
        if len(enemy) != 0:
            api.action_attack(character, random.choice(enemy))
