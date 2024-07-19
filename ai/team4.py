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

    ATTACK_ENEMY = auto()
    """攻擊敵人階段"""


class AiInfo():
    """所有有用到的資料儲存"""

    def __init__(self) -> None:
        self.team_id: int
        """自己的team id"""
        self.fountain: Tower | None = None
        """主堡"""

        self.stage: StageClass = StageClass.START
        """現在的階段"""

        self.target_tower: Tower | None = None
        """要打的塔"""

        # self.target_enemy: Character | None = None
        self.defend_tower: Tower | None = None
        """要防守的塔"""


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
    # 如果找到不屬於自己的中立塔，就從中選一個離主堡（fountain）最近的存起來
    for character in api.get_owned_characters():
        api.action_wander(character)

    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain and tower.team_id != info.team_id]
    if len(others_towers) != 0:
        info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]

# 將所有己方隊伍的士兵移動到某個隨機的位置
    # 一直讓自己的所有士兵在每一個 tick 都找新的一條到遙遠目的的路徑是很花時間的，在後期擁有很多士兵時，這樣的操作很容易超過時限。
    
def action(api: API) :
     for character in api.get_owned_characters():
        api.action_wander(character)
     
     for character in api.get_owned_characters():
        if character.type is CharacterClass.MELEE:
            if character.health <= 400:
                enemies = []
                for enemy in api.get_visible_characters():
                    if enemy.team_id != character.team_id:
                        enemies.append(enemy)
                if len(enemies) >= 1:
                    api.action_attack(api.sort_by_distance(enemies, character.position)[0])

# 將所有己方隊伍的士兵移動到某個隨機的位置
    # 一直讓自己的所有士兵在每一個 tick 都找新的一條到遙遠目的的路徑是很花時間的，在後期擁有很多士兵時，這樣的操作很容易超過時限。
    
# def action() :
#     api.action_move_to(api.get_owned_characters(), pg.Vector2()
#     while api.get_current_time > 30:
#         random.random() * 250, random.random() * 250)

# if  melee_blood <= 400:
#     api.action_attack(api.get_owned_characters(), info.target_tower) 
# if melee_blood:#近戰被塔打一次(-150)



# def stage_explore(api: API):
#     """
#     探索地圖階段，會讓所有的士兵在地圖上亂走。
#     """

#     # while api.get_current_time > 30:
#     change_spawn_by_posibility(api, api.get_owned_towers(), 0.5, 0.5, 0)
#     for character in api.get_owned_characters():
#             api.action_wander(character)

#     # 如果找到不屬於自己的中立塔，就從中選一個離主堡（fountain）最近的存起來
#     # others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain and tower.team_id != info.team_id]
#     # if len(others_towers) != 0:
#     #     info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]


def stage_attack_tower(api: API):
    """
    攻擊塔階段，會讓所有的士兵都去往某個塔走，進行攻擊。
    """
    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.6, 0, 0.4)

    # 攻擊塔
    api.action_move_to(api.get_owned_characters(), info.target_tower.position)
    api.action_attack(api.get_owned_characters(), info.target_tower)


def stage_defend_tower(api: API):
    """
    防禦塔階段，會讓所有的士兵都往某個塔走。
    """
    # 改變塔生成的兵種，讓我們更容易把塔守好！
    for tower in api.get_owned_towers():
        if tower.is_fountain:
            change_spawn_by_posibility(api, [tower], 0, 0, 1)
        else:
            change_spawn_by_posibility(api, [tower], 0.4, 0, 0.6)
    # 往我們要守的塔移動！
    api.action_move_to(api.get_owned_characters(), info.defend_tower.position)

def stage_attack_enemy(api: API):
        enemies = []
        visible = []
        # for character in api.get_visible_characters():
            # if character.team_id != api.get_team_id():
                # visible.append(character)

        for enemy in api.get_visible_characters():
            if enemy.team_id != api.get_team_id():
                enemies.append(enemy)

        for character in api.get_owned_characters():
            target = api.sort_by_distance(enemies, character.position)[0]
            if target.type == CharacterClass.SNIPER:
                api.action_move_and_attack(api.get_owned_characters(), target)
            elif len(visible):
                api.action_move_to(api.get_owned_characters()[1:], visible[0].position)
                api.action_attack(api.get_owned_characters()[1:], visible[0])

def CreateEnemy(api:API):
    my_characters = api.get_owned_characters()
    num, nim = 0, 1
    api.change_spawn_type(api.get_owned_towers()[0], CharacterClass.MELEE)
    for i in my_characters:
        if i.type == CharacterClass.MELEE:
            num += 1
        if i.type == CharacterClass.RANGER:
            nim += 1

    api.send_chat(f"近戰:{num},遠程:{nim}")

    if api.get_current_time() > 20:
        if (num / nim) > 2:
            api.change_spawn_type(api.get_owned_towers()[0], CharacterClass.RANGER)
        else:
            api.change_spawn_type(api.get_owned_towers()[0], CharacterClass.MELEE)
        
    if len(api.get_owned_towers()) != 1:
        for i in range(0, len(api.get_owned_towers())):
            if not api.get_owned_towers()[i].is_fountain:
                tower = api.get_owned_towers()[i]
                api.change_spawn_type(tower, CharacterClass.MELEE)
                nam = 0

                for i in my_characters:
                    if i.type == CharacterClass.SNIPER:
                        nam += 1
                cnt = 0
                for ch in api.get_owned_characters():
                    if (ch.position.distance_to(tower.position)) <= tower.attack_range:
                        if i.type == CharacterClass.SNIPER:
                            cnt += 1
                
                if cnt >= 50:
                    api.change_spawn_type(tower, CharacterClass.MELEE)




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
            # if Tower.health <= 1000:
            #     info.stage = StageClass.ATTACK_TOWER
            # else:
            info.stage = StageClass.ATTACK_TOWER
            # info.stage = StageClass.ATTACK_ENEMY
        

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

    angry_list=['你的程式碼看起來像隨機生成的。',
                    '你寫的程式碼連你自己都不懂吧？',
                    '這段程式碼是你夢遊時寫的嗎？',
                    '你的程式碼有更多BUG還是特性？',
                    '看來你是把錯誤當功能來實現的。',
                    '你的變數命名像是在玩猜謎遊戲。',
                    '你寫的程式碼讓除錯變成恐怖片。',
                    '你的邏輯是用骰子決定的嗎？',
                    '這程式碼像是直接從垃圾箱撿來的。',
                    '你的程式碼需要翻譯才能讀懂。']
    NoTeams = api.get_number_of_teams()
    myScore = api.get_score_of_team(None)
    myRank = 1
    lowestScore = myScore
    myId = api.get_team_id()
    lowestId = myId
    for i in range(1,NoTeams+1):
        if i == myId:
            continue
        if myScore < api.get_score_of_team(i):
            myRank += 1
        if api.get_score_of_team(i) < lowestScore:
            lowestScore = api.get_score_of_team(i)
            lowestId = i
    if myRank != NoTeams and myScore != lowestScore:
        num=random.randint(0,9)
        api.send_chat(f"第{lowestId}隊 {angry_list[num]}")
    else:
        api.send_chat("nevva gonna give u up")