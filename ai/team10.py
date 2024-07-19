"""
Team 10
"""

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
        self.all_ch_id = set()


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
    for character in api.get_owned_characters():
        info.all_ch_id.add(character.id)


def change_spawn_by_posibility(api: API, towers: list[Tower], melee_p: float, ranger_p: float, siniper_p: float):
    """
    機率性改變塔生成的兵種
    """
    assert ((melee_p + ranger_p + siniper_p == 1))
    spawn_type = random.choices([CharacterClass.MELEE, CharacterClass.RANGER, CharacterClass.SNIPER],
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

    for character in api.get_owned_characters():
        api.action_wander(character)

    total = len(info.all_ch_id) % 6
    for tower in api.get_owned_towers():
        if total != 0 and total != 1:
            api.change_spawn_type(tower, CharacterClass.MELEE)
        elif total == 0:
            api.change_spawn_type(tower, CharacterClass.RANGER)
        else:
            api.change_spawn_type(tower, CharacterClass.SNIPER)
    # 如果找到不屬於自己的塔，就存起來
    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]
    if len(others_towers) != 0:
        LL = api.get_grid_size()
        info.target_tower = api.sort_by_distance(others_towers, pg.Vector2(LL//2, LL//2))[0]


def stage_attack_tower(api: API):
    """
    攻擊塔階段，會讓所有的士兵都去往某個塔走，進行攻擊。
    """
    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    for character in api.get_owned_characters():
        api.action_wander(character)

    total = len(info.all_ch_id) % 6
    for tower in api.get_owned_towers():
        if total != 0 and total != 1:
            api.change_spawn_type(tower, CharacterClass.MELEE)
        elif total == 0:
            api.change_spawn_type(tower, CharacterClass.RANGER)
        else:
            api.change_spawn_type(tower, CharacterClass.SNIPER)

    # 攻擊塔
    api.action_move_to(api.get_owned_characters(), info.target_tower.position)
    api.action_attack(api.get_owned_characters(), info.target_tower)


def enemies_near_tower(tower: Tower, api: API):
    """傳入一座塔，回傳塔附近所有視野可及的敵隊士兵"""
    visible_enemies = []  # 創造空列表，存取所有視野可及的敵隊士兵
    for character in api.get_visible_characters():
        if character.team_id != api.get_team_id():
            visible_enemies.append(character)

    near_enemies = []  # 創造空列表，存取所有視野可及，且距離塔 20 單位距離以內的敵隊士兵
    for enemy in visible_enemies:
        enemy = api.refresh_character(enemy)
        if enemy is not None and enemy.position.distance_to(tower.position) <= 20:
            near_enemies.append(enemy)
    return near_enemies


def allies_near_tower(tower: Tower, api: API):
    """傳入一座塔，回傳塔附近所有己方隊伍的士兵"""
    allies = api.get_owned_characters()

    near_allies = []
    for ally in allies:
        if ally.position.distance_to(tower.position) <= 20:
            near_allies.append(ally)
    return near_allies


def find_tower(api: API):
    my_tower = api.get_owned_towers()
    for tower in my_tower:
        if tower.is_fountain == False:
            return tower


def find_fountain(api: API):
    my_tower = api.get_owned_towers()
    for tower in my_tower:
        if tower.is_fountain == True:
            return tower


def calculate_distance(a: pg.Vector2, b: pg.Vector2) -> float:
    return (a-b).length()


def stage_defend_tower(api: API):
    """
    防禦塔階段，會讓所有的士兵都往某個塔走，進行攻擊。
    """
    character_list = []
    for character in api.get_owned_characters():
        api.action_wander(character)

    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]

    own_tower = find_tower(api)
    # 我方士兵大於敵軍，去蹲水晶
    if own_tower is not None and len(enemies_near_tower(own_tower, api)) > len(allies_near_tower(own_tower, api)):
        api.action_wander(api.get_owned_characters())
        min_dis = others_towers[0]
        for x in range(1, len(others_towers)):
            if calculate_distance(others_towers[x], find_fountain) != 0:
                if calculate_distance(min_dis, find_tower(api)) + calculate_distance(min_dis, find_fountain) > calculate_distance(others_towers[x], find_tower(api)) + calculate_distance(others_towers[x], find_fountain):
                    min_dis = others_towers[x]
        change_spawn_by_posibility(api, api.get_owned_towers(), 0.6, 0.4, 0)

        # 攻擊塔
        api.action_move_to(api.get_owned_characters(), min_dis.position)
        api.action_attack(api.get_owned_characters(), min_dis)
    if info.defend_tower is not None:
        api.action_move_to(api.get_owned_characters(), info.defend_tower.position)

    # 改變塔生成的兵種，讓我們更容易把塔守好！
    total = len(info.all_ch_id) % 6
    for tower in api.get_owned_towers():
        if total != 0 and total != 1:
            api.change_spawn_type(tower, CharacterClass.MELEE)
        elif total == 0:
            api.change_spawn_type(tower, CharacterClass.RANGER)
        else:
            api.change_spawn_type(tower, CharacterClass.SNIPER)

    # move(api, api.get_owned_characters(), info.defend_tower.position)
    # 往我們要守的塔移動！
        my_towers = api.get_owned_towers()
    for tower in my_towers:
        if tower.is_fountain:
            position = tower.position
    character_list = []
    for character in api.get_owned_characters():
        distance = character.position.distance_to(tower.position)
        if distance < 10:
            character_list.append(character)
    own_tower = find_tower(api)
    if own_tower is not None and len(enemies_near_tower(own_tower, api)) > len(allies_near_tower(own_tower, api)):
        api.action_move_clear(character_list)
        api.action_move_to(api.get_owned_characters(), info.defend_tower.position)
    else:
        others = []
        for character in api.get_owned_characters():
            if (character not in character_list):
                others.append(character)
        api.action_wander(others)


# def stage_attack_enemy(api: API):
#     """
#     攻擊其他人的階段，會讓所有的士兵都往某個敵對士兵走。
#     """
#     # 如果已經有要攻擊的士兵了
#     pass


info = AiInfo()
cnt = 0


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

        others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]

        # 打下塔了，開始守塔
        if info.target_tower.team_id == info.team_id:
            info.defend_tower = info.target_tower
            info.target_tower = None
            info.stage = StageClass.DEFENCE_TOWER
            own_tower = find_tower(api)
            if len(enemies_near_tower(own_tower, api)) > len(allies_near_tower(own_tower, api)):  # 我方士兵大於敵軍，去蹲水晶
                api.action_wander(api.get_owned_characters())
                min_dis = others_towers[0]
                for x in range(1, len(others_towers)):
                    if calculate_distance(others_towers[x], find_fountain) != 0:
                        if calculate_distance(min_dis, find_tower(api)) + calculate_distance(min_dis, find_fountain) > calculate_distance(others_towers[x], find_tower(api)) + calculate_distance(others_towers[x], find_fountain):
                            min_dis = others_towers[x]
                change_spawn_by_posibility(api, api.get_owned_towers(), 0.6, 0.4, 0)

                # 攻擊塔
                api.action_move_to(api.get_owned_characters(), min_dis.position)
                api.action_attack(api.get_owned_characters(), min_dis)
        if info.defend_tower != None:
            api.action_move_to(api.get_owned_characters(), info.defend_tower.position)

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
    chat_information = ["鹽酥雞 I'm so gay", "你連社交舞都跳不好，還玩什麼遊戲", "梁山伯與ㄊㄞˊ", "我的性別認同是戰鬥直升機", "瑪卡巴卡阿卡哇卡米卡瑪卡姆", "為什麼要偷錢", "素素素素破耨法", "Twerk起來陳總召", "阿笠博士是召部的阿笠博士還是RPG的阿笠博士",
                        "謝謝營姐接跟歌葛格", "花生死掉會變鬼頭刀", "你一定是快斗扮的，滾開！！！"]

    chat_guide = ["就說香菜怕聖光", "芫荽 4 life", "京極真好會學NPCㄛ", "豆花沒加香菜請自己退賽", "你只會打Code，但沒人幫你打Call", "三民主義，吾黨所宗，以建民國，以進大同", "如果袋鼠決定入侵烏拉圭，那麼每一個烏拉圭人都要打14隻袋鼠",
                  "金齁糗😂👍害阮笑到趴在土卡🤣🤣"]
    global cnt
    cnt += 1
    if cnt % 4 == 1:
        api.send_chat(random.choice(chat_information))
    else:
        api.send_chat(random.choice(chat_guide))
