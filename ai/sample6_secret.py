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
    
    ATTACK_ENEMY_CHARACTER_NUM = 17
    ATTACK_ENEMY_CHARACTER_LOWWER = 7

    ATTACK_TOWER_CHARACTER_NUM = 10
    ATTACK_TOWER_CHARACTER_LOWWER = 4
    
    ATTACK_TOWER_CHARACTER_NUM_SECOND = 14
    
    
    TOWER_ATTACK_RANGE = 45
    
    WANDERING_CHARACTER_NUM = 25
    
    

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
        info.target_tower = api.refresh_tower(info.target_tower)
    if info.target_enemy is not None:
        info.target_enemy = api.refresh_character(info.target_enemy)
    if info.fountain is not None:
        info.fountain = api.refresh_tower(info.fountain)

    if info.defend_tower is not None:
        info.defend_tower = api.refresh_tower(info.defend_tower)
        if info.defend_tower.team_id != info.team_id:
            info.defend_tower = None

    api.action_cast_ability(api.get_owned_characters())


def get_min(units: list[Character | Tower], pos: pg.Vector2):
    min_len = (units[0].position - pos).length()
    min_unit = units[0]
    for unit in units:
        if min_len > (unit.position - pos).length():
            min_len = (unit.position - pos).length()
            min_unit = unit
    return min_unit


def move(api: API, chs: list[Character], des: pg.Vector2):
    # api.action_move_to(chs, des)
    for ch in chs:
        if api.get_movement(ch).vector != des:
            api.action_move_to(ch, des)

def change_spawn_by_posibility(api: API, towers: list[Tower] | Tower, melee_p: float, ranger_p: float, siniper_p: float):
    # assert((melee_p + ranger_p + siniper_p))
    if isinstance(towers, Tower):
            towers = [towers]
    spawn_type = random.choices([CharacterClass.MELEE, CharacterClass.RANGER, CharacterClass.SNIPER], \
                                [melee_p, ranger_p, siniper_p])[0]
    for tower in towers:
        api.change_spawn_type(tower, spawn_type)

def stage_start(api: API):
    info.team_id = api.get_team_id()
    info.fountain = api.get_owned_towers()[0]
    # print(f"info.fountain {info.fountain}")

def stage_explore(api: API):
    change_spawn_by_posibility(api, api.get_owned_towers(), 1, 0, 0)
    
    for character in api.get_owned_characters()[3:]:
        api.action_wander(character)

    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]
    if len(others_towers) != 0:
        info.target_tower = get_min(others_towers, info.fountain.position)

def stage_attack_tower(api: API):
    # move(api, api.get_owned_characters(), info.target_tower.position)
    # api.action_move_to(api.get_owned_characters(), info.target_tower.position)
    # api.action_attack(api.get_owned_characters(), info.target_tower)

    for tower in api.get_owned_towers():
        if tower.is_fountain:
            change_spawn_by_posibility(api, tower, 0.8, 0.2, 0)
        else:
            change_spawn_by_posibility(api, tower, 0.5, 0.3, 0.2)
    if len(api.get_owned_characters()) > info.ATTACK_TOWER_CHARACTER_NUM:
        move(api, api.get_owned_characters(), info.target_tower.position)
    elif len(api.get_owned_characters()) < info.ATTACK_TOWER_CHARACTER_LOWWER:
        if info.defend_tower is not None:
            move(api, api.get_owned_characters(), info.defend_tower.position)
        else:
            move(api, api.get_owned_characters(), info.fountain.position)
    # else:
    #     move(api, api.get_owned_characters(), info.target_tower.position)


def stage_defend_tower(api: API):
    for tower in api.get_owned_towers():
        if not tower.is_fountain:
            change_spawn_by_posibility(api, [tower], 0.4, 0, 0.6)
        else:
            change_spawn_by_posibility(api, [tower], 1, 0, 0)

    if info.defend_tower is not None:
        move(api, api.get_owned_characters(), info.defend_tower.position)
    else:
        move(api, api.get_owned_characters(), info.fountain.position)


def stage_attack_enemy(api: API):
    for tower in api.get_owned_towers():
        if tower.is_fountain:
            change_spawn_by_posibility(api, tower, 0.6, 0.3, 0.1)
        else:
            change_spawn_by_posibility(api, tower, 0.2, 0.2, 0.6)

    enemies = [character for character in api.get_visible_characters() if character.team_id != info.team_id]

    # if info.target_enemy is not None:
    #     info.target_enemy = None

    if len(enemies) != 0:
        if info.target_enemy is None:
            if info.defend_tower is not None:
                info.target_enemy = get_min(enemies, info.defend_tower.position)
            else:
                info.target_enemy = get_min(enemies, info.fountain.position)

        for ch in api.get_owned_characters():
            nearest_enemy = get_min(enemies, ch.position)
            if (nearest_enemy.position -  ch.position).length() < 8:
                move(api, [ch], nearest_enemy.position)
            else:
                move(api, [ch], info.target_enemy.position)
                # api.action_attack(ch, nearest_enemy)
            # if len(enemies) != 0:
            #     # print(enemies)
            #     nearest_enemy = get_min(enemies, ch.position)
            #     if (nearest_enemy.position -  ch.position).length() < 8:
            #         move(api, [ch], nearest_enemy.position)
            #         api.action_attack(ch, nearest_enemy)
            #     else:
            #         move(api, api.get_owned_characters(), info.target_enemy.position)
    elif len(api.get_owned_characters()) > info.WANDERING_CHARACTER_NUM:
        api.action_wander(api.get_owned_characters()[:10])
    elif info.defend_tower is not None:
        move(api, api.get_owned_characters(), info.defend_tower.position)
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

    for character in api.get_owned_characters():
        enemy = api.within_attacking_range(character)
        if len(enemy) != 0:
            api.action_attack(character, random.choice(enemy))
    
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

        if info.target_tower.team_id == info.team_id:
            info.defend_tower = info.target_tower
            info.target_tower = None
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

        if info.defend_tower is not None and info.defend_tower.health < 0.3 * info.defend_tower.max_health:
            info.stage = StageClass.DEFENCE_TOWER
        # elif info.defend_tower is not None and len(api.get_owned_characters()) < info.ATTACK_ENEMY_CHARACTER_LOWWER:
        #     info.stage = StageClass.DEFENCE_TOWER
        elif info.target_tower is not None and info.target_tower.team_id != info.team_id:
            info.stage = StageClass.ATTACK_TOWER

        # elif info.target_tower is None:
        #     min_length: int = 100000
        #     min_tower: Tower = None
        #     for tower in api.get_visible_towers():
        #         if (not tower.is_fountain) and tower.team_id != info.team_id:
        #             if min_length > (tower.position - info.fountain.position).length():
        #                 min_length = (tower.position - info.fountain.position).length()
        #                 min_tower = tower
        #     if min_tower is not None and len(api.get_owned_characters()) > info.ATTACK_TOWER_CHARACTER_NUM_SECOND:
        #         info.target_tower = min_tower
        #         info.stage = StageClass.ATTACK_TOWER
        #     else:
        #         info.target_tower = None

    else:
        print("wrong stage")
        info.stage = StageClass.EXPLORE


    for ch in api.get_owned_characters():
        for tower in api.get_visible_towers():
            if tower.is_fountain and tower.team_id != info.team_id and \
                (tower.position - ch.position).length() < info.TOWER_ATTACK_RANGE + 5:
                api.action_move_clear(ch)
                break

