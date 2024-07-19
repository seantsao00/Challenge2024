"""
Team 6
"""

import math
import random

import pygame as pg

from api.prototype import *
ct = 0
my_melee = []
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
        self.my_characters: list[Character] = []


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
    for character in info.my_characters:
        if character.type is CharacterClass.MELEE:
            my_melee.append(character)
    info.my_characters = api.get_owned_characters()
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


def stage_explore(api: API, free_allies:list):
    """
    探索地圖階段，會讓所有的士兵在地圖上亂走。
    """
    # 讓主堡生成
    change_spawn_by_posibility(api, api.get_owned_towers(), 1, 0, 0)
    visable_enemy = []
    for character in free_allies:
        api.action_wander(character)
        for i in api.get_visible_characters():
            if i not in api.get_owned_characters():
                visable_enemy.append(i)

        for vis in visable_enemy:
            if isinstance(vis, Tower) and api.refresh_tower(vis) is not None:
                api.action_attack(character, api.refresh_tower(vis))
            elif isinstance(vis, Character) and api.refresh_character(vis) is not None:
                api.action_attack(character, api.refresh_character(vis))

    # 如果找到不屬於自己的塔，就存起來
    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]
    if len(others_towers) != 0:
        info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]


def stage_attack_tower(api: API):
    """
    攻擊塔階段，會讓所有的士兵都去往某個塔走，進行攻擊。
    """
    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.2, 0.8, 0)
    my_characters = api.get_owned_characters()
    # 攻擊塔
    api.action_move_to(api.get_owned_characters(), api.refresh_tower(info.target_tower).position) # need target tower
    api.action_attack(api.get_owned_characters(), api.refresh_tower(info.target_tower))

def stage_defend_tower(api: API):
    """
    防禦塔階段，會讓所有的士兵都往某個塔走，進行攻擊。
    """ 
    # 改變塔生成的兵種，讓我們更容易把塔守好！
    for tower in api.get_owned_towers():
        if tower.is_fountain:
            change_spawn_by_posibility(api, [tower], 0.6, 0.4, 0)
        else:
            change_spawn_by_posibility(api, [tower], 0, 0, 1)
    
    
    if  len(my_melee)>= 15:
        if tower.is_fountain:
            change_spawn_by_posibility(api, [tower], 0, 1, 0)
        else:
            change_spawn_by_posibility(api, [tower], 0, 0.3, 0.7)
        for character in my_melee:
            if api.refresh_character(character) is not None:
                api.action_wander(api.refresh_character(character))
    detect_defending_allies(api)


    # move(api, api.get_owned_characters(), info.defend_tower.position)
    # 往我們要守的塔移動！
    api.action_move_to(detect_defending_allies(api), info.defend_tower.position)

# def stage_attack_enemy(api: API):
#     """
#     攻擊其他人的階段，會讓所有的士兵都往某個敵對士兵走。
#     """
#     # 如果已經有要攻擊的士兵了
#     pass


info = AiInfo()



def detect_nearby_allies(api: API, point:Character):
    
    nearby_allies=[]
    for i in api.sort_by_distance(api.get_owned_characters(), api.refresh_character(point).position):
    # for i in api.get_visible_characters():
        if i in api.get_owned_characters() and (i.position - point.position).length < 20:
            nearby_allies.append(i)
            if len(nearby_allies) >= 15:
                stage_attack_tower(api)

    
def detect_defending_allies(api: API):
    defending_allies = []
    free_allies = []
    for character in api.get_owned_characters():
        distance = (api.refresh_character(character).position - api.refresh_tower(info.defend_tower).position).length()
        sorted_allies = api.sort_by_distance(api.get_owned_characters(), info.defend_tower.position)
        for i in sorted_allies:
            if len(defending_allies) <= 14 and (api.refresh_character(i).position - api.refresh_tower(info.defend_tower).position).length() < 10 :
                defending_allies.append(i)
        for character in api.get_owned_characters():
            if character not in defending_allies:
                free_allies.append(character)
        if len(defending_allies) >= 15:
            stage_explore(api, free_allies)
    
    return defending_allies
        

        




def every_tick(api: API):
    """
    一定要被實作的 function ，會定期被遊戲 call
    在使用 VS Code 寫 code 的時候可以把滑鼠移到變數、函數上方，看它們的詳細解說。
    在使用 VS Code 寫 code 的時候可以按住 Ctrl 再用滑鼠點擊變數、函數，來跳轉到與它們相關的地方。
    在測試的時候可以只放一隻 ai 、在執行時一次加很多 arguments (如 -qrp)。
    """
    global ct
    update(api)

    if info.stage == StageClass.START:
        stage_start(api)
        print(f"team {info.team_id} is on stage START")
        info.stage = StageClass.EXPLORE

    if info.stage == StageClass.EXPLORE:
        print(f"team {info.team_id} is on stage EXPLORE")
        for i in api.get_owned_characters():
            distance = (api.refresh_character(i).position - api.refresh_tower(info.fountain).position).length()
            if distance <= 20:
                detect_nearby_allies(api, i)
                break
        
        if ct == 0:
            stage_explore(api, api.get_owned_characters())
        

        # 找到塔後，偵測友軍數量，大於15個友軍就去打塔，有bug
        if info.target_tower is not None: 
            nearby_allies=[]
            for i in api.get_owned_characters():
                nearby_allies.append(i)
                if len(nearby_allies) >= 10:
                    ct = 1
                    api.action_move_clear(api.get_owned_characters())
                    info.stage = StageClass.ATTACK_TOWER
                    break

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

    chat_use = [

        '只探視野不會贏 QQ',

        '我好喜歡資訊營',

        '加油加油！',

        '最新一集劇場版的結局是...',

        '好餓...想吃宵夜了...',

        'Bug 退散！',

        '維護良好素質，從你我做起！',

        '為什麼 sample 好像有點強 @@',

        '菜就多練，輸不起就別玩',

        '大破防',

        '笑死，還敢來喔',

        '快認輸吧',

        'damn',

        'ranger拌42號混凝土',

        '第一次打code喔，太菜了吧',

        '吃虧是福？那我祝你福如東海',

        '老鐵666',

        '注意看，這個人太狠了ㄏ',

        '我們超有料啊',

        '你誰啊？吵什麼',

        '作為失敗的典型，你太成功了',

        '聽說有人把sample直接拿出來比賽',

        '歡迎加入芫荽教',

        '加入芫荽，人生會發光',

        'M3 4 life',

        '六小六小六小 六六六',

        '.六小一出手，對手全閃躲',

        '敢與六小戰，馬上跪著看',

        '六小來挑釁，對手全認命',

        '六小打全服，對手全跪服',

        '六小贏乾脆，對手去下跪',

        '輸了咱六小，就不要出現在我的視線，很礙眼，不差你一個對手',

        '當弱者必須要有弱者的風範，立即滾下臺',

        '六小是什麼咖，是你贏不起的咖',

        '池水退了，就知道誰沒穿泳褲',

        '你們為什麼整天想當小丑，一直出醜',

        '看到你心慌了，別太燥',

        '看看鏡子中的你，請你不要太為你的弱小而傷心了',

        '不要寫一些破程式，很好笑的。',

        '何處望對手?滿眼風光黃泉中',

        '敵營浪費多少時，潸潸，不僅兵卒排排送',

        '對戰時期敵紛紛，敵方陣營欲斷魂',

        '借問敵手何處有，牧童遙指靈堂墳',

        '敵人奪得勝利日，家祭無忘告乃翁',

        '敵手不識勝滋味，裝無不能。裝無不能。為贏六小強說勝。',

        '竹杖芒鞋輕勝馬，誰怕？六小陣營必得勝。',

        '敵方猿聲啼不住，六小已過萬重難。',

        '就這'






    ]

   

    # 以 Const.CHAT_PROBABILITY 的機率隨便說說話

    #if random.uniform(0, 1) < Const.CHAT_PROBABILITY:

    api.send_chat(random.choice(chat_use))
