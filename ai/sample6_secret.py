import math
import random

import pygame as pg

from api.prototype import *


class StageClass(IntEnum):
    START = auto()
    EXPLORE = auto()
    ATTACK_TOWER = auto()
    DEFENCE_TOWER = auto()
    ATTACK_ENEMY = auto()


class AiInfo():
    EXPLORE_TIME_LIMT = 30
    ATTACK_ENEMY_CHARACTER_NUM = 15

    def __init__(self) -> None:
        self.team_id: int
        self.fountain: Tower | None = None

        self.stage: StageClass = StageClass.START

        self.target_tower: Tower | None = None
        self.target_enemy: Character | None = None
        self.defend_tower: Tower | None = None

        self.tower_id_to_entity: dict = {}
        self.character_id_to_entity: dict = {}

def update(api: API):
    for tower in api.get_visible_towers():
        info.tower_id_to_entity[tower.id] = tower
    for character in api.get_visible_characters():
        info.character_id_to_entity[character.id] = character

    if info.target_tower is not None:
        info.target_tower =info.tower_id_to_entity[info.target_tower.id]
    if info.target_enemy is not None:
        info.target_enemy = info.character_id_to_entity[info.target_enemy.id]
    if info.fountain is not None:
        info.fountain = info.tower_id_to_entity[info.fountain.id]
    if info.defend_tower is not None:
        info.defend_tower = info.tower_id_to_entity[info.defend_tower.id]
    
    api.action_cast_ability(api.get_owned_characters())

def move(api: API, chs: list[Character], des: pg.Vector2):
    for ch in chs:
        if api.get_movement(ch).vector != des:
            api.action_move_to(ch, des)
            
def change_by_posibility(api: API, towers: list[Tower], melee_p: float, ranger_p: float, siniper_p: float):
    assert(melee_p + ranger_p + siniper_p == 1)
    spawn_type = random.choices([CharacterClass.MELEE, CharacterClass.RANGER, CharacterClass.SNIPER], \
                                [melee_p, ranger_p, siniper_p])[0]
    for tower in towers:
        api.change_spawn_type(tower, spawn_type)

def stage_start(api: API):
    info.team_id = api.get_team_id()
    info.fountain = api.get_owned_towers()[0]
    # print(f"info.fountain {info.fountain}")

def stage_explore(api: API):
    change_by_posibility(api, [info.fountain], 1, 0, 0)
    for character in api.get_owned_characters():
        api.action_wander(character)

    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]
    if len(others_towers) != 0:
        info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]

def stage_attack_tower(api: API):
    move(api, api.get_owned_characters(), info.target_tower.position)
    # api.action_move_to(api.get_owned_characters(), info.target_tower.position)
    api.action_attack(api.get_owned_characters(), info.target_tower)
    if info.target_tower.team_id == info.team_id:
        info.defend_tower = info.target_tower
        info.target_tower = None

def stage_defend_tower(api: API):
    for tower in api.get_owned_towers():
        if not tower.is_fountain:
            change_by_posibility(api, [tower], 0.4, 0, 0.6)
        else:
            change_by_posibility(api, [tower], 1, 0, 0)

    move(api, api.get_owned_characters(), info.defend_tower.position)
    # api.action_move_to(api.get_owned_characters(), info.defend_tower.position)

def stage_attack_enemy(api: API):
    enemies = [character for character in api.get_visible_characters() if character.team_id != info.team_id]
    if info.target_enemy is not None and info.target_enemy.id not in info.character_id_to_entity:
        info.target_enemy = None
    if len(enemies) != 0:
        info.target_enemy = api.sort_by_distance(enemies, info.fountain.position)[0]
        move(api, api.get_owned_characters(), info.target_enemy.position)
    # api.action_move_to(api.get_owned_characters(), info.fountain.position)
    elif info.defend_tower is not None:
        move(api, api.get_owned_characters(), info.defend_tower)
    else:
        move(api, api.get_owned_characters(), info.fountain)
        


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

        if info.target_tower is not None:
            info.stage = StageClass.ATTACK_TOWER
        elif api.get_current_time() >= info.EXPLORE_TIME_LIMT:
            info.stage = StageClass.ATTACK_ENEMY

    elif info.stage == StageClass.ATTACK_TOWER:
        print(f"team {info.team_id} is on stage ATTACK_TOWER")
        stage_attack_tower(api)

        if info.target_tower is None:
            info.stage = StageClass.DEFENCE_TOWER
        # elif api.get_current_time() >= info.EXPLORE_TIME_LIMT:
        #     info.stage = StageClass.ATTACK_ENEMY

    elif info.stage == StageClass.DEFENCE_TOWER:
        print(f"team {info.team_id} is on stage DEFENCE_TOWER")
        stage_defend_tower(api)

        if info.target_tower is not None and info.target_tower.team_id != api.get_team_id():
            info.stage = StageClass.ATTACK_TOWER
        if len(api.get_owned_characters()) > info.ATTACK_ENEMY_CHARACTER_NUM:
            info.stage = StageClass.ATTACK_ENEMY

    elif info.stage == StageClass.ATTACK_ENEMY:
        print(f"team {info.team_id} is on stage ATTACK_ENEMY")
        stage_attack_enemy(api)
            
        if info.defend_tower.health < 0.5 * info.defend_tower.max_health:
            info.stage = StageClass.DEFENCE_TOWER
        elif info.defend_tower is not None and len(api.get_owned_characters()) < 10:
            info.stage = StageClass.DEFENCE_TOWER
        elif info.target_tower is not None and info.target_tower.team_id != info.team_id:
            info.stage = StageClass.ATTACK_TOWER

    else:
        print("wrong stage")
        info.stage = StageClass.EXPLORE

    for character in api.get_owned_characters():
        
        enemy = api.within_attacking_range(character)
        if len(enemy) != 0:
            api.action_attack(character, random.choice(enemy))
