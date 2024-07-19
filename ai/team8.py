"""
第八小隊
"""

import math
import random

import pygame as pg

from api.prototype import *

from view.object.nyan import NyanView
from model import Nyan
from event_manager import *
import util

class Const:
    CHAT_PROBABILITY: float = 0.05
    """隨便說說話的機率"""

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
        self.fountain: Tower | None = None

        self.stage: StageClass = StageClass.START

        self.target_tower: Tower | None = None
        self.target_enemy: Character | None = None
        self.defend_tower: Tower | None = None
        self.defend_tower2: Tower | None = None

def calculate_distance(a: pg.Vector2, b: pg.Vector2) -> float:
    """計算兩點之間的距離(可以用向量減法理解)"""
    return (a-b).length()

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
    if info.target_enemy is not None:
        info.target_enemy = api.refresh_character(info.target_enemy)

    # 開技能
    #api.action_cast_ability(api.get_owned_characters())


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

def change_route(api: API):
    for character in api.get_owned_characters():
        destination = pg.Vector2(-1,-1)
        i=0
        while api.get_terrain(destination) != MapTerrain.ROAD and i < 30:
            detination = pg.Vector2(random.random() * 250, random.random() * 250)
            i+=1
            print('A')
        if destination != pg.Vector2(-1,-1):
            api.action_move_to(character, destination)

def stage_explore(api: API):
    """
    探索地圖階段，會讓所有的士兵在地圖上亂走。
    """
    # 讓主堡生成
    change_spawn_by_posibility(api, api.get_owned_towers(), 1, 0, 0)
    for character in api.get_owned_characters():
        api.action_wander(character)
        # 若遇到障礙物
        if api.get_terrain(character.position) == MapTerrain.OBSTACLE or api.get_terrain(character.position) == MapTerrain.OFFROAD:
            destination = pg.Vector2(-1,-1)
            i=0
            while api.get_terrain(destination) != MapTerrain.ROAD and i < 30:
                detination = pg.Vector2(random.random() * 250, random.random() * 250)
                i+=1
            if destination != pg.Vector2(-1,-1):
                api.action_move_to(character, destination)
        #若遇到敵方士兵，開打
        attack(api)


    # 如果找到不屬於自己的塔，就存起來
    others_towers = []
    for tower in api.get_visible_towers():
        if tower.team_id != api.get_team_id() and not tower.is_fountain:
            others_towers.append(tower)
    if len(others_towers) != 0:
        info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]

def stage_attack_tower(api: API):
    """
    攻擊塔階段，會讓所有的士兵都去往某個塔走，進行攻擊。
    """
    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    if info.target_tower.team_id == 0:
        change_spawn_by_posibility(api, api.get_owned_towers(), 0.6, 0.4, 0)
    else:
        tower_can_attack = []
        for tower in api.get_visible_towers():
            if not tower.is_fountain and tower.team_id != api.get_team_id():
                tower_can_attack.append(tower)
        if (tower_can_attack):
            tower_can_attack = api.sort_by_distance(tower_can_attack, api.get_owned_towers()[0].position)
            info.target_tower = tower_can_attack[0]
        change_spawn_by_posibility(api, api.get_owned_towers(), 0.5, 0.3, 0.2)
    # 確保近戰兵數量到達一定程度/時間經過調整機率，增加狙擊手加快攻塔，不夠則調回原機率

    # 攻擊塔
    if info.target_tower is not None:
        api.action_move_to(api.get_owned_characters(), info.target_tower.position)
        for character in  api.within_attacking_range(info.target_tower, api.get_owned_characters()):
            #若遇到敵方士兵，開打
            attack(api)
            if character.type == CharacterClass.MELEE:
                api.action_cast_ability(character)
            elif character.type == CharacterClass.RANGER:
                if calculate_distance(character.position, info.target_tower.position)<=15:
                    api.action_cast_ability(character)
            else:
                if calculate_distance(character.position, info.target_tower.position)<=40:
                    api.action_move_clear(character)
                    api.action_cast_ability(character)
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

    # 往我們要守的塔移動！
    api.action_move_to(api.get_owned_characters(), info.defend_tower.position)

get_target_tower = False

def stage_attack_enemy(api: API):
    """
    攻擊其他人的階段，會讓部分的士兵都往某個敵對士兵走。
    """
    global get_target_tower
    attack(api)
    for tower in api.get_owned_towers():
        if tower.is_fountain:
            change_spawn_by_posibility(api, [tower], 1, 0, 0)
        else:
            change_spawn_by_posibility(api, [tower], 0.4, 0.4, 0.2)
    for tower in api.get_visible_towers():
        if tower.team_id != api.get_team_id() and not tower.is_fountain:
            get_target_tower = True
            info.target_tower=tower
            
            api.action_move_to(api.get_owned_characters(), info.target_tower.position)
            for character in  api.within_attacking_range(info.target_tower, api.get_owned_characters()):
                #若遇到敵方士兵，開打
                attack(api)
                if character.type == CharacterClass.MELEE:
                    api.action_cast_ability(character)
                elif character.type == CharacterClass.RANGER:
                    if calculate_distance(character.position, info.target_tower.position)<=15:
                        api.action_cast_ability(character)
                else:
                    if calculate_distance(character.position, info.target_tower.position)<=40:
                        api.action_move_clear(character)
                        api.action_cast_ability(character)
            api.action_attack(api.get_owned_characters(), info.target_tower)
        if not get_target_tower:
            for character in api.get_owned_characters():
                if api.get_movement(character) != MovementStatusClass.WANDERING:
                    api.action_wander(character)
                attack(api)

def attack(api: API):
    enemies = []
    for character in api.get_visible_characters():
        if character.team_id != api.get_team_id():
            enemies.append(character)
    for character in api.get_owned_characters():
        enemy = api.within_attacking_range(character, enemies)
        if len(enemy) != 0:
            api.sort_by_distance(enemy, character.position)
            api.action_attack(character, enemy[0])
    


info = AiInfo()

messages = [
"你這個傻逼，真不要臉！",
"你有病啊？別來煩我！",
"你這種人就是欠揍。",
"別跟我廢話，有本事出來單挑啊！",
"別以為你很厲害，我看你就是個王八蛋！",
"你這鳥人，別來煩我！",
"少在我面前賣弄，你不就是個小屁孩嗎？",
"你真是缺德，天天跟我要東要西。",
"你這樣做是不是有病啊？",
"我真是服了你這樣的人了，無聊透頂！",
"你這個ONE BOY!",
"你超床",
"English or spanish?",
"我去，老铁666啊!",
"一波骚操作啊",
"火箭刷起来",
"谢谢小哥哥的火箭!",
"你个老六",
"喜歡你的第一年我還沒有告白",
"不啾喔",
"帥帥帥",
"你的裝備是在淘寶買的嗎?",
"可以不要拉低平均智商嗎?",
"對不起~太弱了沒注意到~",
"但換來的是你無情的拒絕",
"Damn~~~~~~~",
"救火其實是滅火",
"兩個字其實是三個字",
"生魚片其實是死魚片?",
"可以不要一直放水嗎?",
"我好(乾)愛(你)你(娘)",
"地圖掌控程度:就哥倫布一樣",
"咖啡算是一種豆漿嗎?",
"欲窮千里目，挖洗哩老木",
"吃麻婆豆腐會被麻婆罵嗎?",
"近親不能結婚，為什麼我爸爸可以娶我媽媽?",
"空腹不能喝牛奶，那剛出生的小羊為什麼沒餓死",
"分一半其實是分兩半",
"黑人穿黑絲是黑絲還是肉絲?",
"一個半小時其實三十分鐘",
"為什麼修車的叫黑手，洗錢的叫車手?",
"每天都有好多人要上班，班的老婆不會生氣嗎?",
"小星星跟字母歌有一樣的旋律",
"千年神樹算一種超齡老木嗎?",
"超自然其實是超不自然",
"台灣的狗跟美國的狗講話，要用台灣狗語還是美國狗語",
"去看醫生其實是被醫生看",
"兄弟轉身有急事",
"兄弟...",
"你們是不是找不到彩蛋?",
"你們有蛋蛋，但沒有彩蛋",
"機比機比加八加八",
"呀勒呀勒，沒有彩蛋的大小姐",
"毛利偵探事務所已落後1000分",
"美國的蜜蜂算是一種USB",
"不要低頭，皇冠會掉",
"不要流淚，必取會笑",
"陽光，必取，海浪，澎湖灣還有一位老船長",
"喜歡你噎",
"sheesh sheesh sheesh sheesh sheesh sheesh~",
"M3~"

]


def every_tick(api: API):
    """
    一定要被實作的 function ，會定期被遊戲 call
    在使用 VS Code 寫 code 的時候可以把滑鼠移到變數、函數上方，看它們的詳細解說。
    在使用 VS Code 寫 code 的時候可以按住 Ctrl 再用滑鼠點擊變數、函數，來跳轉到與它們相關的地方。
    在測試的時候可以只放一隻 ai 、在執行時一次加很多 arguments (如 -qrp)。
    """
    enemies = []
    for character in api.get_visible_characters():
        if character.id != api.get_team_id():
            enemies.append(character)
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
        if len(api.within_attacking_range(info.defend_tower, enemies)) == 0:
            info.stage = StageClass.ATTACK_ENEMY

    elif info.stage == StageClass.ATTACK_ENEMY:
        print(f"team {info.team_id} is on stage ATTACK_ENEMY")
        stage_attack_enemy(api)
        if (enemies):
            if info.defend_tower.health < 750:
                if len(api.within_attacking_range(info.defend_tower, enemies)):
                    info.stage = StageClass.DEFENCE_TOWER
    else:
        print("wrong stage")
        info.stage = StageClass.EXPLORE

    # 設定所有人都會攻擊某一個目標，邊走邊攻擊！
    for character in api.get_owned_characters():
        enemy = api.within_attacking_range(character)
        if len(enemy) != 0:
            api.action_attack(character, random.choice(enemy))


    chat_choices = messages
    # 以 Const.CHAT_PROBABILITY 的機率隨便說說話
    if random.uniform(0, 1) < Const.CHAT_PROBABILITY:
        api.send_chat(random.choice(chat_choices))