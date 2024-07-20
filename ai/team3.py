"""
第三小隊
"""
 
import math
import random
 
import pygame as pg
 
from api.prototype import *
 
start_time = 0
 
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
 
    EXPLORE2_TOWER = auto()
    """增廣視野"""
 
    ATTACK_TOWER2 = auto()
    DEFENCE_TOWER2 = auto()
 
    # ATTACK_ENEMY = auto()
    # """攻擊敵人階段"""
 
 
class AiInfo():
    """所有有用到的資料儲存"""
 
    def __init__(self) -> None:
        self.team_id: int
        self.fountain: Tower | None = None
 
        self.stage: StageClass = StageClass.START
 
        self.target_tower: Tower | None = None
        self.target_tower2: Tower | None = None
        # self.target_enemy: Character | None = None
        self.defend_tower: Tower | None = None
        self.defend_tower2: Tower | None = None
 
 
 
 
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
    if info.target_tower2 is not None:
        info.target_tower2 = api.refresh_tower(info.target_tower2)
    if info.defend_tower2 is not None:
        info.defend_tower2 = api.refresh_tower(info.defend_tower2)
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
 
def assign_random_destination(character: Character, api: API):
    """指定一個還沒有開視野的隨機位置給 character ，且這個位置不是障礙物。"""
    new_destination = pg.Vector2(random.uniform(0, api.get_grid_size() - 1),
                                 random.uniform(0, api.get_grid_size() - 1))
    i = 0
    while api.is_visible(new_destination) or api.get_terrain(new_destination) is MapTerrain.OBSTACLE:
        new_destination = pg.Vector2(random.uniform(0, api.get_grid_size() - 1),
                                     random.uniform(0, api.get_grid_size() - 1))
        i += 1
        if i == 10:  # 最多嘗試 10 次
            break
    api.action_move_to(character, new_destination)
 
def stage_start(api: API):
    """
    最開始的階段，會對某些變數初始化。
    """
    info.team_id = api.get_team_id()
    info.fountain = api.get_owned_towers()[0]
 
 
 
def stage_explore(api: API):
    print("stage explore")
    """
    探索地圖階段，會讓所有的士兵在地圖上亂走。
    """
    # 讓主堡生成
    change_spawn_by_posibility(api, api.get_owned_towers(), 1, 0, 0)
 
    for character in api.get_owned_characters():  # 用 for 迴圈遍歷所有自己的士兵
        if api.get_movement(character).status is MovementStatusClass.STOPPED:  # 這個士兵停止移動了
            stick = random.random()  # 抽個籤
            if stick < 0.5:  # 讓角色去探索沒有視野的地方
                assign_random_destination(character, api)
            else:  # 讓角色開始隨意亂走
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
    change_spawn_by_posibility(api, api.get_owned_towers(), 0, 1, 0)
 
 
    # 攻擊塔
    """
    attack_characters = []
    attack_towers = []
    for character in api.get_owned_characters():
        if character.id % 3 == 0:
            attack_characters.append(character)
        else:
            attack_towers.append(character)
    """
    api.refresh_tower(info.target_tower)
    api.action_move_to(api.get_owned_characters(), info.target_tower.position)
    for character in api.get_owned_characters():    
        if character.type != CharacterClass.RANGER:
            api.action_cast_ability(character)
        else:
            api.action_cast_ability(character, position=info.target_tower.position)
    api.action_attack(api.get_owned_characters(), info.target_tower)
 
 
def stage_attack_tower2(api: API):
    """
    攻擊塔階段，會讓所有的士兵都去往某個塔走，進行攻擊。
    """
    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    change_spawn_by_posibility(api, api.get_owned_towers(), 0, 1, 0)
 
 
    # 攻擊塔
    api.refresh_tower(info.target_tower2)
    api.action_move_to(api.get_owned_characters(), info.target_tower2.position)
    for character in api.get_owned_characters():    
        if character.type != CharacterClass.RANGER:
            api.action_cast_ability(character)
        else:
            api.action_cast_ability(character, position=info.target_tower2.position)
    api.action_attack(api.get_owned_characters(), info.target_tower2)
 
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
    melee = []
    ranger = []
    sniper = []
    for character in api.get_owned_characters():
        if character.type == CharacterClass.MELEE:
            melee.append(character)
        elif character.type == CharacterClass.RANGER:
            ranger.append(character)
        else:
            sniper.append(character)
 
    api.action_wander(melee)
    for i in range(len(ranger)):
        if i >= len(melee):
            api.action_wander(ranger[i])
        else:
            api.action_move_to(ranger[i], melee[i].position)
    api.action_move_to(sniper, info.defend_tower.position)
 
    for character in api.get_owned_characters():
        enemy_characters = []
        for ch in api.get_visible_characters():
            if ch.team_id != api.get_team_id():
                enemy_characters.append(ch)
 
        api.sort_by_distance(enemy_characters, character.position)
        if len(enemy_characters):
            api.action_attack(character, enemy_characters[0])
 
 
def stage_defend_tower2(api: API):
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
    melee = []
    ranger = []
    sniper = []
    for character in api.get_owned_characters():
        if character.type == CharacterClass.MELEE:
            melee.append(character)
        elif character.type == CharacterClass.RANGER:
            ranger.append(character)
        else:
            sniper.append(character)
 
    api.action_wander(melee)
    for i in range(len(ranger)):
        if i >= len(melee):
            api.action_wander(ranger[i])
        else:
            api.action_move_to(ranger[i], melee[i].position)
    api.action_move_to(sniper, info.defend_tower2.position)
 
    for character in api.get_owned_characters():
        enemy_characters = []
        for ch in api.get_visible_characters():
            if ch.team_id != api.get_team_id():
                enemy_characters.append(ch)
 
        api.sort_by_distance(enemy_characters, character.position)
        if len(enemy_characters):
            api.action_attack(character, enemy_characters[0])
 
 
# def stage_attack_enemy(api: API):
#     """
#     攻擊其他人的階段，會讓所有的士兵都往某個敵對士兵走。
#     """
#     # 如果已經有要攻擊的士兵了
#     pass
 
def explore2_tower(api:API):
    print("explore2_tower")
    change_spawn_by_posibility(api, api.get_owned_towers(), 1, 0, 0)
 
    for character in api.get_owned_characters():  # 用 for 迴圈遍歷所有自己的士兵
        if api.get_movement(character).status is MovementStatusClass.STOPPED:  # 這個士兵停止移動了
 
            stick = random.random()  # 抽個籤
            if stick < 0.5:  # 讓角色去探索沒有視野的地方
                assign_random_destination(character, api)
            else:  # 讓角色開始隨意亂走
                api.action_wander(character)
 
 
    # 如果找到不屬於自己的塔，就存起來
    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain and tower.team_id != api.get_team_id()]
    others_towers = api.sort_by_distance(others_towers, info.fountain.position)
    for tower in others_towers:
        if tower.team_id != api.get_team_id():
            info.target_tower2 = tower
            break
 
 
 
info = AiInfo()
 
 
def every_tick(api: API):
    """
    一定要被實作的 function ，會定期被遊戲 call
    在使用 VS Code 寫 code 的時候可以把滑鼠移到變數、函數上方，看它們的詳細解說。
    在使用 VS Code 寫 code 的時候可以按住 Ctrl 再用滑鼠點擊變數、函數，來跳轉到與它們相關的地方。
    在測試的時候可以只放一隻 ai 、在執行時一次加很多 arguments (如 -qrp)。
    """
    global start_time
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
            start_time = api.get_current_time()
            info.stage = StageClass.DEFENCE_TOWER
 
    elif info.stage == StageClass.ATTACK_TOWER2:
        print(f"team {info.team_id} is on stage ATTACK_TOWER")
        stage_attack_tower2(api)
 
 
 
        # 打下塔了，開始守塔
        if info.target_tower2.team_id == info.team_id:
            info.defend_tower2 = info.target_tower2
            info.target_tower2 = None
            start_time = api.get_current_time()
            info.stage = StageClass.DEFENCE_TOWER2
 
 
 
    elif info.stage == StageClass.DEFENCE_TOWER:
        print(f"team {info.team_id} is on stage DEFENCE_TOWER")
 
        stage_defend_tower(api)
 
        if (api.get_current_time()-start_time) >= 10:
            info.stage = StageClass.EXPLORE2_TOWER
 
        # 塔被人打下了，打回來！
        if info.defend_tower is not None and info.defend_tower.team_id != api.get_team_id():
            info.target_tower = info.defend_tower
            info.stage = StageClass.ATTACK_TOWER
 
    elif info.stage == StageClass.DEFENCE_TOWER2:
        print(f"team {info.team_id} is on stage DEFENCE_TOWER")
 
        stage_defend_tower2(api)
 
        if (api.get_current_time()-start_time) >= 10:
            info.stage = StageClass.EXPLORE2_TOWER
 
        # 塔被人打下了，打回來！
        if info.defend_tower2 is not None and info.defend_tower2.team_id != api.get_team_id():
            info.target_tower2 = info.defend_tower2
            info.stage = StageClass.ATTACK_TOWER2
        # if ...你認為可以開始打人的時候:
 
        #     info.stage = StageClass.ATTACK_ENEMY
 
    # elif info.stage == StageClass.ATTACK_ENEMY:
    #     print(f"team {info.team_id} is on stage ATTACK_ENEMY")
        # stage_attack_enemy(api)

    elif info.stage == StageClass.EXPLORE2_TOWER:
        print(f"team {info.team_id} is on stage EXPLORE")
        explore2_tower(api)
        print(info.target_tower)
        if info.target_tower2 is not None:
            info.stage = StageClass.ATTACK_TOWER2
 
 
    else:
        print("wrong stage")
        info.stage = StageClass.EXPLORE
 
    # 設定所有人都會攻擊某一個目標，邊走邊攻擊！
    for character in api.get_owned_characters():
        enemy = api.within_attacking_range(character)
        if len(enemy) != 0:
            api.action_attack(character, random.choice(enemy))
 
    api.send_chat(random.choice(["小丑讀大學讀什麼系? 你跟他沒戲...", 
                                "對阿，海狗是水汪汪 @csw.agger", 
                                "對阿，海狗是水汪汪 @csw.agger", 
                                "失去很多也得到很多 珍惜所有勇敢去闖 @uber0802", 
                                "失去很多也得到很多 珍惜所有勇敢去闖 @uber0802", 
                                "封心鎖愛 捲毛除外 @tekai324_yen", 
                                "甚麼都是假的只有我每天買點吃的喝的哄著自己才是真的", 
                                "我會考上成大 成功沒大學",
                                "台中人比較兇是因為Taichung動嗎", 
                                "只是懶了點 @edmond_0908",
                                "@_bt.68_n 記得追蹤", 
                                "@uber0802 記得追蹤",
                                "以聽團之名行暈船之實 這誰", 
                                "兄弟這則刪了唄，我是無所謂的，", 
                                "沒那麼容易破防的，但是我一個朋友可能有點汗流浹背了，", 
                                "他不太舒服想睡了，當然不是我哈，我一直都是行的，", 
                                "以一個旁觀者的心態看吧，也不至於破防吧", 
                                "最美召部 @trs4630", 
                                "最美召部 @trs4630", 
                                "尛", 
                                "芫荽 4 life", 
                                "SOPHIA!!!!!!!! @tzuch1n",
                                "全世界最堅強的19歲少年 @524.zc", 
                                "我們是三小你們是三小", 
                                "三小三小三小，三三三!!!!", 
                                "但我不會寫程式 @mk0214._.a", 
                                "中森青子好美 @ssstanleyyy._.0302", 
                                "@2024ntucsiecamp", 
                                "家都被偷了還去打架阿", 
                                "程式寫了一晚上，不如我們茜姊的十分鐘",
                                "國立台灣大學指彈吉他社男公關 @ryan.cyt_", 
                                "HBD金牌銷售部大台北地區北投分支石牌組總經理 @ryan.cyt_", 
                                "屏東人的魔鬼步伐 @脆姊",
                                "茜姊拿的不是結營證書，是臺大保送證書", 
                                "• <-這是慶記哥單手抓住的子彈", 
                                "再半年就學測了，怎麼還在打瓦羅蘭", 
                                "我剛睡醒什麼意思 @雄哥", 
                                "恢復生活品質 @peiiiii_0919",
                                "爛梗超爛 @沁姊",
                                "咖喱飯拌不拌都沒差 反正晚上睡覺也是沒有伴", 
                                "我的佔有慾真的很強…每次看到別人的錢，我都覺得那個是我的", 
                                "比如說，當一個女生說：「我不想談戀愛」時，「和你」這兩個字，是不發音的", 
                                "我優點很多，但有一個缺點，缺點你", 
                                "你能不能好好走路，都撞上我的心了", 
                                "距離不是問題，你離我不夠近才是問題", 
                                "我做事十拿九穩，缺你一吻", 
                                "我知道你是哪裡人，我的心上人", 
                                "今天頭暈一天，可能想你想過頭了", 
                                "只許州官放火，不許你離開我", 
                                "我終於知道為什麼我總感冒了，因為我對你毫無抵抗力", 
                                "每次過安檢我總是過不去，他們說我心里裝著一個你", 
                                "不思進取，思你",
                                "有被爛到，謝謝沁姊",
                                "喜歡你，噎", 
                                "很好，隊輔，你已經成功吸引我的注意",
                                "隊輔，你在玩火", 
                                "像你們這樣的隊輔，我見多了"]))
 
 
 