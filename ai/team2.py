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
    """攻擊塔階段(中立)"""

    DEFENSE_TOWER = auto()
    """防禦塔階段"""

    ATTACK_ENEMY_TOWER = auto()
    """攻擊塔階段(敵方)"""

def chat(api: API) -> None:
    lyrics = {0: "笑死_我根本沒把你們放在眼裡_因為我放在心裡啦_哈哈哈",
        2: "你真的很麻煩_但我偏偏愛找麻煩_",
        4: "哈哈哈ㄌㄩㄝˉ",
        6: "心態穩住就可以得到你囉_ㄩㄇ",
        8: "我真的很花心_喜歡每一種你",
        10: "喔不!_我掉進河裡了_我們的愛河裡",
        12: "如果我跟你媽一起掉進海裡_你先救誰??",
        14: "曖昧讓人受盡委屈",
        16: "我這個人什麼都可以抵擋_除了你家的人頭",
        18: "你就像我的內褲_極為重要",
        20: "流著淚怎麼睡得著",
        22: "漁夫每次活動都要站中間_因為他有sea味",
        24: "你知道嗎_當你受傷時_你會痛",
        26: "欸_你知道嗎_閉上眼睛你就會甚麼都看不到",
        28: "一邊做數學_一邊罵髒話的行為可以視為在對數學講dirty_dalk",
        30: "今天很嗆是吧",
        32: "暴力不能解決事情_但可以解決你",
        34: "我認真起來_連我自己都會怕",
        36: "每次照鏡子的時候都會被自己漂亮到",
        38: "看好了世界_我只示範一次",
        40: "怎麼了_不開心嗎?_說出來讓我們開心一下叭",
        42: "你長得很好看ㄟ_只是不明顯而已",
        44: "如果你沒有長得不好看的話其實你也長得蠻好看的",
        46: "對不起,我的錯",
        48: "我們只能在中午見面_不然我早晚會愛上你",
        50: "看到你這張臉_我還是比較喜歡我的",
        52: "你是獨一無二的_因為我們都不希望再有第二個",
        54: "在哪裡跌到_就在哪裡躺下",
        56: "我優點很多_但有一個缺點_缺點你",
        58: "距離不是問題_你離我不夠近才是問題",
        60: "近朱者赤_近你者甜",
        62: "你可以笑一個嗎_我的咖啡忘記加糖了",
        64: "我有兩個心願_在你身邊和你在身邊",
        66: "落葉歸根_我歸你",
        68: "你很累吧_在我腦海裡跑了一整天",
        70: "我是9你是3_我除了你還是你",
        72: "和你猜拳我只出剪刀_因為你是我的拳布",
        74: "你臉上有點東西_有點好看",
        76: "我最近一直覺得很困_為你所困",
        78: "你喜歡水的話_那你已經喜歡上70%的我了",
        80: "除了你的美色_不接受任何賄賂",
        82: "派迪好帥_我愛派迪",
        84: "我在台大為派迪打call",
        86: "Happy_超級可愛",
        88: "愷欣開心嗎好開心好開心好開心",
    }
    song_time = int(api.get_current_time()) % 89
    if song_time in lyrics:
        api.send_chat(lyrics[song_time])

class AiInfo():
    """所有有用到的資料儲存"""

    def __init__(self) -> None:
        self.team_id: int
        self.fountain: Tower | None = None
        self.stage: StageClass = StageClass.START
        self.target_tower: Tower | None = None
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

    # 開技能
    api.action_cast_ability(api.get_owned_characters())

def calculate_distance(a: pg.Vector2, b: pg.Vector2) -> float:
    """計算兩點之間的距離(可以用向量減法理解)"""
    return (a-b).length()


def change_spawn_by_posibility(api: API, towers: list[Tower], melee_p: float, ranger_p: float, siniper_p: float):
    """
    機率性改變塔生成的兵種
    """
    assert ((melee_p + ranger_p + siniper_p == 1))
    spawn_types = random.choices([CharacterClass.MELEE, CharacterClass.RANGER, CharacterClass.SNIPER],
                                [melee_p, ranger_p, siniper_p])[0]
    for tower in towers:
        api.change_spawn_type(tower, spawn_types)


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

def get_nearby_fellows(api: API, position: pg.Vector2, distance: int = 50) -> list[Character]:
    """
    拿到距離某點附近(距離 distance 內)友軍的 list，如果沒有特別指定 distance 的話預設是 50。
    """
    my_character = api.get_owned_characters()
    nearby_fellows = []
    for character in my_character:
        if calculate_distance(character.position, position) <= distance:
            nearby_fellows.append(character)
    return nearby_fellows


def stage_attack_tower(api: API):
    """
    攻擊塔階段，會讓所有的士兵都去往某個塔走，進行攻擊。
    """
    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.5, 0.4, 0.1)

    # 攻擊塔
    enemy_list=[]
    for character in api.get_visible_characters():
        if character.team_id != api.get_team_id() and calculate_distance(info.target_tower.position,character.position)<=25:
            enemy_list.append(character)
        api.action_move_and_attack(api.get_owned_characters(), info.target_tower)

def get_visible_enemies(api: API) -> tuple[list[Tower], list[Character]]:
    """找出視野範圍內的可攻擊目標。回傳一個`tuple(tower的list, character的list)`"""
    my_team_id = api.get_team_id()

    visible_enemy_towers = []
    visible_towers = api.get_visible_towers()
    for tower in visible_towers:
        if tower.team_id != my_team_id:
            visible_enemy_towers.append(tower)

    visible_enemy_characters = []
    visible_characters = api.get_visible_characters()
    for character in visible_characters:
        if character.team_id != my_team_id:
            visible_enemy_characters.append(character)

    return (visible_enemy_towers, visible_enemy_characters)


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
    characters = api.get_owned_characters()
    api.action_move_to(characters[:min(7, len(characters))], info.defend_tower.position)
    if len(characters) > 7:
        visible = []
        for character in api.get_visible_characters():
            if character.team_id != api.get_team_id():
                visible.append(character)
        for char in characters[7:]:
            visible = api.sort_by_distance(visible, char.position)
            if len(visible):
                api.action_move_and_attack(char,visible[0])

def stage_attack_enemy(api: API):
    characters = api.get_owned_characters()
    api.action_move_and_attack(characters, info.target_tower)


#     """
#     攻擊其他人的階段，會讓所有的士兵都往某個敵對士兵走。
#     """
#     # 如果已經有要攻擊的士兵了
#     pass

def spawn_type(api: API):
    if info.target_tower is None or info.target_tower.team_id == 0:
        change_spawn_by_posibility(api, api.get_owned_towers(), 0.5, 0.4, 0.1)
    else:
        change_spawn_by_posibility(api, api.get_owned_towers(), 0.2, 0.5, 0.3)

def tower_spawn_type(api: API):
    my_towers = api.get_owned_towers()
    my_characters = api.get_owned_characters()
    for tower in my_towers:
        count=0
        if tower.is_fountain:
            continue
        for character in reversed(my_characters):
            if calculate_distance(tower.position,character.position)<=40 and character.type is CharacterClass.SNIPER:
                count+=1
        if count < 7:
            change_spawn_by_posibility(api, [tower], 0.5, 0.3, 0.2)
        else:
            change_spawn_by_posibility(api, [tower], 0, 0, 1)


info = AiInfo()


def every_tick(api: API):
    """
    一定要被實作的 function ，會定期被遊戲 call
    在使用 VS Code 寫 code 的時候可以把滑鼠移到變數、函數上方，看它們的詳細解說。
    在使用 VS Code 寫 code 的時候可以按住 Ctrl 再用滑鼠點擊變數、函數，來跳轉到與它們相關的地方。
    在測試的時候可以只放一隻 ai 、在執行時一次加很多 arguments (如 -qrp)。
    """
    update(api)
    spawn_type(api)
    tower_spawn_type(api)


    if info.stage == StageClass.START:
        stage_start(api)
        print(f"team {info.team_id} is on stage START")
        info.stage = StageClass.EXPLORE

    if info.stage == StageClass.EXPLORE:
        print(f"team {info.team_id} is on stage EXPLORE")
        stage_explore(api)

        # 找到塔後，向塔攻擊
        if info.target_tower is not None:
            info.stage = StageClass.ATTACK_TOWER #轉換階段

    elif info.stage == StageClass.ATTACK_TOWER:
        print(f"team {info.team_id} is on stage ATTACK_TOWER")
        stage_attack_tower(api)

        # 打下塔了，開始守塔
        info.target_tower = api.refresh_tower(info.target_tower)
        if info.target_tower.team_id == info.team_id:
            info.defend_tower = info.target_tower
            info.target_tower = None
            info.stage = StageClass.DEFENSE_TOWER

    elif info.stage == StageClass.DEFENSE_TOWER:
        print(f"team {info.team_id} is on stage DEFENCE_TOWER")
        stage_defend_tower(api)

        # 塔被人打下了，打回來！
        info.defend_tower = api.refresh_tower(info.defend_tower)
        if info.target_tower is not None and info.target_tower.team_id != api.get_team_id():
            info.target_tower = info.defend_tower
            info.stage = StageClass.ATTACK_ENEMY_TOWER

    elif info.stage == StageClass.ATTACK_ENEMY_TOWER:
        print(f"team {info.team_id} is on stage ATTACK_ENEMY")
        stage_attack_enemy(api)
        info.defend_tower = api.refresh_tower(info.defend_tower)
        if info.defend_tower is not None and info.defend_tower.team_id == api.get_team_id():
            info.target_tower = info.defend_tower
            info.stage = StageClass.DEFENSE_TOWER
        #attack enemy階段所要做的事&轉換到其他階段時機
    else:
        print("wrong stage")
        info.stage = StageClass.EXPLORE

    # 設定所有人都會攻擊某一個目標，邊走邊攻擊！
    for character in api.get_owned_characters():
        enemy = api.within_attacking_range(character)
        if len(enemy) != 0:
            api.action_attack(character, min(enemy, key=lambda x: x.health))

    chat(api)