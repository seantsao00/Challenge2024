# 第七小隊
import math
import random

import pygame as pg

from api.prototype import *

zuipao = [
    "封心所愛，踢K大哥哥除外",
    "我們敲胸的",
    "去吃pupu啦",
    "打那麼爛是要去當越南移工嗎",
    "超ㄏ",
    "有手就行",
    "輕輕鬆鬆",
    "菜就多練",
    "輸不起就別玩",
    "破房",
    "Danmmm",
    "M3",
    "阿偉好帥",
    "選修物理可以教我物理嗎",
    "蔡侑岑可以不要再罵我ㄍㄋㄋ了嗎",
    "張必成的口技跟我們這組一樣屌逼逼",
    "張聲元可以幫我們聲援嗎",
    "我們派出eraser 把你們努力過的痕跡都擦掉",
    "王禹吉吉跳舞好燒(騷)",
    "映辰姐用他的美麗把大家美爛",
    "黃政漢不要感冒",
    "香蕉你個芭樂",
    "弱雞",
    "怎麼有一股菜味",
    "踢K大哥哥不要再宿醉了",
    "嚴常憲好帥",
    "怎麼有狗在吠",
    "啊不就好厲害",
    "繼續，我看你能玩出什麼花樣",
    "芫荽 4 life",
    "不是吧不是吧 就這點能耐",
    "香蕉逼逼槍，射進你心房",
    "不要丟人現眼啦~",
    "這波操作辣眼睛",
    "老鐵遛六六",
    "English or Spanish",
    "Damn不要亂碰東西",
    "Yo battle",
    "菜雞玩意ㄦ"
]


def every_tick(api: API):
    if api.get_map_name() == "ntu" or api.get_map_name() == "field":
        every_tick1(api)
    else:
        every_tick2(api)


def every_tick1(api: API):
    visible_character = []
    visible_tower = []
    for character in api.get_visible_characters():
        if character.team_id != api.get_team_id():
            visible_character.append(character)
    for tower in api.get_visible_towers():
        if not tower.is_fountain:
            if tower.team_id != api.get_team_id():
                visible_tower.append(tower)

    # 讓己方隊伍一個的士兵繞著圓圈移動
    character = api.get_owned_characters()[0] if len(api.get_owned_characters()) > 0 else None
    # 這個士兵停止移動了
    if character is not None and api.get_movement(character).status is MovementStatusClass.STOPPED:
        api.action_wander(character)
    print(len(visible_character))
    print(len(visible_tower))

    my_characters = api.get_owned_characters()
    if len(visible_character):  # 若視野內存在敵方士兵
        api.action_cast_ability(my_characters)  # 不管三七二十一把技能打開
        if len(visible_tower) == 0:
            for character in my_characters:
                api.action_move_to(character, visible_character[0].position)
                api.action_attack(character, visible_character[0])
        else:
            for character in my_characters:
                if character.id % 2 == 0:
                    api.action_move_to(character, visible_character[0].position)
                    api.action_attack(character, visible_character[0])
                else:
                    api.action_move_to(character, visible_tower[0].position)
                    api.action_attack(character, visible_tower[0])
    elif len(visible_tower):
        api.action_cast_ability(my_characters)
        my_characters = api.get_owned_characters()
        for character in my_characters:
            api.action_move_to(character, visible_tower[0].position)
            api.action_attack(character, visible_tower[0])
    api.send_chat(zuipao[int(random.random() * len(zuipao))])


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

    SEARCH_TOWER_2 = auto()
    """防禦塔階段"""

    ATTACK_TOWER_2 = auto()

    # ATTACK_ENEMY = auto()
    # """攻擊敵人階段"""

    DEFEND = auto()


class AiInfo():
    """所有有用到的資料儲存"""

    def __init__(self) -> None:
        self.team_id: int
        self.fountain: Tower | None = None

        self.stage: StageClass = StageClass.START

        self.target_tower: Tower | None = None
        self.target_tower_2: Tower | None = None

        self.defend_tower: Tower | None = None
        self.search_tower: Tower | None = None
        self.search_tower2: Tower | None = None


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
    if info.target_tower_2 is not None:
        info.target_tower = api.refresh_tower(info.target_tower_2)
    # if info.target_enemy is not None:
    #     info.target_enemy = api.refresh_character(info.target_enemy)

    # 開技能
    # api.action_cast_ability(api.get_owned_characters())


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
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.6, 0.4, 0)
    for character in api.get_owned_characters():
        api.action_wander(character)

    # 如果找到不屬於自己的塔，就存起來

    # others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain and tower.team_id != info.team_id]

    # if len(others_towers)>=1:
    #     info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]
    # if len(others_towers)>=2:
    #     info.target_tower_2 = api.sort_by_distance(others_towers, info.fountain.position)[1]
    others_towers = []
    for tower in api.get_visible_towers():
        if not tower.is_fountain:
            others_towers.append(tower)

    if len(others_towers) >= 1:
        info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]
    if len(others_towers) >= 2:
        info.target_tower_2 = api.sort_by_distance(others_towers, info.fountain.position)[1]


def stage_attack_tower(api: API):

    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.3, 0.7, 0)

    MELEE = []
    RANGER = []
    SNIPER = []
    target_tower = []
    target_enemy = []
    for tower in api.get_visible_towers():
        if tower != api.get_owned_towers():
            target_tower.append(tower)
    for enemy in api.get_visible_characters():
        if enemy != api.get_owned_characters():
            target_enemy.append(enemy)
    for character in api.get_owned_characters():
        if character.type == CharacterClass.MELEE:
            MELEE.append(character)
        elif character.type == CharacterClass.RANGER:
            RANGER.append(character)
        else:
            SNIPER.append(character)
    # MELEE
    api.action_cast_ability(MELEE)
    api.action_move_to(MELEE, info.target_tower.position)
    api.action_attack(MELEE, info.target_tower)
    # RANGER
    api.action_move_to(RANGER, info.target_tower.position)
    api.action_attack(RANGER, info.target_tower)
    for r in RANGER:
        RANGER_target = api.within_attacking_range(r, target_tower)
        if len(RANGER_target) != 0:
            api.action_cast_ability(r)


def stage_search_tower_2(api: API, character_search, character_defence):
    print('inside search tower 2')
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.5, 0.3, 0.2)

    api.action_wander(character_search)
    api.action_move_to(character_defence, info.defend_tower.position)
    enemies = []
    for en in api.get_visible_characters():
        if en != api.get_owned_characters():
            enemies.append(en)

    for character in character_defence:
        if character.position.distance_to(info.defend_tower.position) <= 10:
            if character.type is CharacterClass.MELEE:
                api.action_move_along(api.get_owned_characters()[:1],
                                      pg.Vector2(3 * math.cos(api.get_current_time() / 20),
                                                 3 * math.sin(api.get_current_time() / 20)))
            nearest_target = api.sort_by_distance(enemies, info.defend_tower.position)[0]
            api.action_attack(character, nearest_target)
        if character.type is CharacterClass.SNIPER:
            api.action_move_along(api.get_owned_characters()[:1],
                                  pg.Vector2(2 * math.cos(api.get_current_time() / 20),
                                             2 * math.sin(api.get_current_time() / 20)))
            nearest_target = api.sort_by_distance(enemies, info.defend_tower.position)[0]
            api.action_attack(character, nearest_target)

    # 如果找到不屬於自己的塔，就存起來
    # others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]

    others_towers = []
    for tower in api.get_visible_towers():
        if not tower.is_fountain:
            others_towers.append(tower)

    if len(others_towers) >= 2:
        info.target_tower_2 = others_towers[1]
        return True
    else:
        return False


def stage_attack_tower_2(api: API, character_defence, character_attack):

    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.3, 0.7, 0)

    MELEE = []
    RANGER = []
    SNIPER = []
    target_tower = [info.target_tower_2]

    for tower in api.get_visible_towers():
        if tower != api.get_owned_towers():
            target_tower.append(tower)

    for character in character_attack:
        if character.type == CharacterClass.MELEE:
            MELEE.append(character)
        elif character.type == CharacterClass.RANGER:
            RANGER.append(character)
        else:
            SNIPER.append(character)
    # MELEE
    api.action_cast_ability(MELEE)
    api.action_move_to(MELEE, info.target_tower_2.position)
    api.action_attack(MELEE, info.target_tower_2)
    # RANGER
    api.action_move_to(RANGER, info.target_tower_2.position)
    api.action_attack(RANGER, info.target_tower_2)
    for r in RANGER:
        RANGER_target = api.within_attacking_range(r, target_tower)
        if len(RANGER_target) != 0:
            api.action_cast_ability(r)

    api.action_move_to(character_defence, info.defend_tower.position)


info = AiInfo()


def every_tick2(api: API):
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
        print(api.get_current_time())
        if api.get_current_time() > 10:
            print('start explore')
            info.stage = StageClass.EXPLORE

    elif info.stage == StageClass.EXPLORE:
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

            others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]
            if len(others_towers) >= 2:
                info.target_tower_2 = api.sort_by_distance(
                    others_towers, info.fountain.position)[1]

                info.stage = StageClass.ATTACK_TOWER_2
            else:
                info.search_tower = None
                info.stage = StageClass.SEARCH_TOWER_2

    elif info.stage == StageClass.SEARCH_TOWER_2:
        print(f"team {info.team_id} is on stage SEARCH_TOWER_2")
        character_defence = []
        character_search = []
        for ch in api.get_owned_characters():
            if ch.id % 3 == 0:
                character_defence.append(ch)
            else:
                character_defence.append(ch)

        found = stage_search_tower_2(api, character_search, character_defence)

        # 塔被人打下了，打回來！
        if info.defend_tower is not None and info.defend_tower.team_id != api.get_team_id():
            info.target_tower = info.defend_tower
            info.stage = StageClass.ATTACK_TOWER
        if found is True:
            info.stage = StageClass.ATTACK_TOWER_2
    elif info.stage == StageClass.ATTACK_TOWER_2:
        print(f"team {info.team_id} is on stage ATTACk_TOWER_2")

        character_defence = []
        character_attack = []
        for i in range(len(api.get_owned_characters())):
            if api.get_owned_characters()[i].id % 3 == 0:
                character_defence.append(api.get_owned_characters()[i])
            else:
                character_attack.append(api.get_owned_characters()[i])

        stage_attack_tower_2(api, character_defence, character_attack)

        if info.defend_tower is not None and info.defend_tower.team_id != api.get_team_id():
            info.target_tower = info.defend_tower
            info.stage = StageClass.ATTACK_TOWER

        my_towers = api.get_owned_towers()
        if len(my_towers) >= 3:
            info.stage = StageClass.DEFEND

    elif info.stage == StageClass.DEFEND:

        character_defence_1 = []
        character_defence_2 = []
        for i in range(len(api.get_owned_characters())):
            if api.get_owned_characters()[i].id % 2 == 0:
                character_defence_1.append(api.get_owned_characters()[i])
            else:
                character_defence_2.append(api.get_owned_characters()[i])

        api.get_owned_towers()

        api.action_move_to(character_defence_1, api.get_owned_towers()[0].position)
        api.action_move_to(character_defence_2, api.get_owned_towers()[1].position)

    else:
        print("wrong stage")
        info.stage = StageClass.EXPLORE

    enemies = []
    for en in api.get_visible_characters():
        if en != api.get_owned_characters():
            enemies.append(en)

    my_character = api.get_owned_characters()
    for k in range(len(my_character)):
        if len(api.within_attacking_range(my_character[k], enemies)) > 0:
            api.action_cast_ability(my_character[k])
            api.action_attack(my_character[k], api.within_attacking_range(
                my_character[k], enemies)[0])
            print('attack')
    api.send_chat(zuipao[int(random.random() * len(zuipao))])
