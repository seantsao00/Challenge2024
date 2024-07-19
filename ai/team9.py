#九小

import math
import random

import pygame as pg

from api.prototype import *

########################################

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

    ATTACK_ENEMY_TOWER = auto()
    """反擊階段"""

    DEFENCE_TOWER = auto()
    """防禦塔階段"""

    TOWER_ATTACK_ENEMY = auto()
    """有塔時攻擊敵人階段"""

###################################################

novel_count = 0
novel = '''
22歲，你大學畢業了，因為你的專業並不好找工作。
頭幾年你沒找到工作,宅在家中，
忍受著孤獨和父母的抱怨。
24歲，你找到工作了，
工作薪水並不高，
還要經常加班到深夜。
30歲，你結婚了，
對象是媒人介紹的，
父母問你喜歡那個姑娘麼，
你愣了愣說：“喜歡吧。”
33歲，你因為身體越來越差，
加班越來越少，
晉升的速度也越來越緩慢。
那天下班，老婆告訴你：
“孩子要上幼兒園了，
雙語的一個月10000。”
你皺了皺眉頭，那邊就已經不耐煩了，
“隔壁的老王家孩子，一個月15000！”
“你已經這樣了，你想讓孩子也輸？！”
你沒說話，回屋給老婆轉了15000塊錢，
這筆錢，你原本打算給自己過個生日，買個新顯卡。
36歲，孩子上了一年級。
老師說一年級最關鍵，打好基礎很重要，
你笑著說，是是是，老師您多照顧，
新生接待的老師看著你不明事理的臉，
給你指了一條明路：
“課外輔導班，一個月8000。”
38歲的時候，孩子上了三年級。
老師說，三年級，最關鍵，承上啟下很重要。
你笑著說：“是是是，正打算再報個補習班。”
42歲，孩子上了國中。
有一天回到家，她對你說：“
爸爸，我想學鋼琴。”
你沒什麼猶豫的。
你以為這些年，你已經習慣了。
但那句“爸爸現在買不起”你始終說不出口。
好在孩子比較懂事，她說：“爸爸沒事，要不我先學陶笛也可以。
你看著這麼懂事的孩子，卻開心不起來。
44歲，孩子上了一個不好不差的高中。
有一天你在開會，接到了老師的電話
，電話里說你的孩子在學校打架了，
叫你去一趟 。
你唯唯諾諾的。
和那個比你還小5歲的領導請了個假，
到學校又被老師訓了一通，
無非台詞就是那一句：
“你們做家長的就知道工作，能不能陪陪孩子？”
你看著這個老師，有點可笑，
因為他好像以前說：
“家長在外辛苦點，
多賺點錢讓孩子多補補課。”現在的他好像和以前的他不是一個人
48歲，孩子上了大學。
很爭氣，是一個好學校，
她學的專業你有點看不懂，
你只知道工作不一定好找，
而且學費還死貴。
你和她深夜想聊聊，
準備了一瓶高粱，一碟花生米，
你說著那些曾經你最討厭的話，
還是要為以後工作著想
挑個熱門的專業
活著比熱愛重要
你們從交流變成了爭吵。
你發現，你老了，
老到可能都說不過這個18歲的孩子。
你說不過她，只能說一句：“我是你爸爸！”
孩子看著你，知道再怎麼爭辯都沒用，
這場確立你最後威嚴的酒局不歡而散，
你聽的不真切。
在孩子回自己屋的路上好像叨叨了一句：
“我不想活的像你一樣。”
你怎麼就哭了呢？50歲的人了，
一定是酒太辣了，對不對？
一定是酒太辣了。
55歲，孩子工作了，似乎有一點理解你了，
但你卻反了過來，你說不要妥協。
56歲，孩子也結婚了。
你問她喜歡那個年輕人麼。
她果斷地說：“喜歡吧。”
你很欣慰。
60歲，辛苦了一輩子，你想出去走走。
身邊的那個人過了30年，
你依舊分不清到底喜不喜歡，
你們開始規劃旅游路線。
這麼多年了，
你們還是存在分歧，還是在爭吵，
某個瞬間，你覺得，
這樣可能也挺好。
當一切都準備好了。
女兒說：“爸媽，我們工作太忙了，
可以幫我們照顧一下孩子麼？”
你們退了機票，又回到了30年前，
70歲，孩子的孩子也長大了，
不用天天操心了 。
你下定決心說：“一定要去玩一趟 。”
可是手邊的拐杖 ，
只能支持你走到樓下的花園。
73歲，你在醫院的病床上 ，從昏迷中醒來，
身邊聚滿了人，
你迷迷糊糊的看見醫生搖了搖頭，
周圍那些人神情肅穆。
你明白了，你要死掉了，
你沒有感到一絲害怕 ，
你突然問自己，
我到底是什麼時候死掉的呢？
你想起30歲的那場婚禮 ，
原來，那時候，你就死掉了吧。
依照慣例，死前的3秒，
你的大腦要走馬燈，倒敘你這73個年頭的一生，畫面一張一張的過
1秒、2秒、兩秒過去了，你面無表情的看著這兩秒內的回憶。
第3秒，突然你笑了。
原來已經回到了15歲的那一年，你看見一個男孩，他拿著一瓶牛奶
背著書包，後面跟著一群男孩，
那個男孩從另一個女孩家的陽臺下跑過，
他朝窗戶里看了看，
那是15歲的你暗戀的那個女孩子，
你想不起來她長什麼樣子了，
最後一秒你努力的回憶著，
3秒過去了，身邊的人突然間開始嚎啕大哭，你可能聽不清了，
你最後想起了一個畫面，要是當時有簽下去就好了...
中華民國國軍是一個積極新創、人才齊全、戰鬥兵力雄厚、訓練特
色鮮明的部隊，在國際上具有重要影響力與競爭力，在多個領域具
有非常前瞻的科技實力，擁有世界一流的武器裝備與師資力量，各
種排名均位於全球前列，並且擁有公開透明的升遷管道、各種進修
資源，以及婚喪生育補助可以申請，歡迎大家報考志願役！
國軍人才招募專線：0800-000-050
'''
novel = novel.split()

class AiInfo():
    """所有有用到的資料儲存"""

    def __init__(self) -> None:
        self.team_id: int
        self.fountain: Tower | None = None

        self.stage: StageClass = StageClass.START

        self.target_tower: Tower | None = None
        self.target_enemy: Character | None = None
        self.defend_tower: Tower | None = None

        self.siege_targets: list[Character | Tower] = []

info = AiInfo()

########################################################

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
    api.action_cast_ability(api.get_owned_characters())

############################################################

def change_spawn_by_posibility(api: API, towers: list[Tower], melee_p: float, ranger_p: float, siniper_p: float):
    """
    機率性改變塔生成的兵種
    """
    assert ((melee_p + ranger_p + siniper_p == 1))
    spawn_type = random.choices([CharacterClass.MELEE, CharacterClass.RANGER, CharacterClass.SNIPER],
                                [melee_p, ranger_p, siniper_p])[0]
    for tower in towers:
        api.change_spawn_type(tower, spawn_type)


##############################################################

def stage_start(api: API):
    """
    最開始的階段，會對某些變數初始化。
    """
    info.team_id = api.get_team_id()
    info.fountain = api.get_owned_towers()[0]
    info.novel = novel
    info.novel_count = novel_count

#################################################################

def stage_explore(api: API):
    """
    探索地圖階段，會讓所有的士兵在地圖上亂走。
    """
    # 讓主堡生成
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.8, 0.2, 0)
    for character in api.get_owned_characters():
        api.action_wander(character)

    # 如果找到不屬於自己的塔，就存起來
    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain]
    if len(others_towers) != 0:
        info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]

###################################################################

def stage_attack_tower(api: API):
    """
    攻擊塔階段，會讓所有的士兵都去往某個塔走，進行攻擊。
    """
    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.7, 0.3, 0)

    # 攻擊塔
    api.action_move_and_attack(api.get_owned_characters(), info.target_tower)

#######################################################################

def stage_defend_tower(api: API):
    """
    防禦塔階段，會讓所有的士兵都往某個塔走，進行攻擊。
    """
    # 改變塔生成的兵種，讓我們更容易把塔守好！
    for tower in api.get_owned_towers():
        if tower.is_fountain:
            change_spawn_by_posibility(api, [tower], 1, 0, 0)
        else:
            change_spawn_by_posibility(api, [tower], 0.2, 0.2, 0.6)
    if info.target_tower is not None:
        api.action_move_to(api.get_owned_characters(), info.target_tower.position)

#########################################################################

def stage_attack_enemy_tower(api: API):
    """
    反擊階段，會讓所有的士兵攻擊敵人在打塔
    """
    if info.target_enemy is None:
        others_enemies = api.get_visible_characters()
        for enemies_id in others_enemies:
            if enemies_id.team_id != info.team_id:
                info.target_enemy = enemies_id
#    my_charactor = [enemies for enemies in api.get_visible_characters()]
 #   for nearest_siege_target in 
  #  nearest_siege_target = api.sort_by_distance(info.siege_targets,)[0]

    for tower in api.get_owned_towers():
        change_spawn_by_posibility(api, [tower], 0.4, 0.3, 0.3)

    for ch in api.get_owned_characters():
        if ch.type == CharacterClass.SNIPER and info.target_enemy is not None:
            api.action_attack(ch, info.target_enemy)
        elif info.target_tower is not None:
            api.action_attack(ch, info.target_tower)

    if info.target_tower is not None:
        api.action_move_and_attack(api.get_owned_characters(), info.defend_tower)

#########################################################################

def stage_tower_attack_enemy(api: API):
    """
    游擊階段，會讓一部分的士兵游擊
    """
    if info.target_enemy is None:
        others_enemies = [enemies for enemies in api.get_visible_characters()]
        for enemies_id in others_enemies:
            if enemies_id.team_id != info.team_id:
                info.target_enemy = enemies_id
    
    # if info.target_enemy is None:
    #     api.send_chat(f"target enemy is None! ;w;")

    for tower in api.get_owned_towers():
        if tower.is_fountain:
            change_spawn_by_posibility(api, [tower], 0.8, 0.2, 0)
        else:
            change_spawn_by_posibility(api, [tower], 0.2, 0.2, 0.6)

    for ch in api.get_owned_characters():
        if ch.type == CharacterClass.SNIPER and info.target_enemy is not None:
            api.action_attack(ch, info.target_enemy)
        elif info.target_tower is not None:
            api.action_attack(ch, info.target_tower)

    if info.target_enemy is not None:
        api.action_move_and_attack(api.get_owned_characters(), info.target_enemy)

###########################################################################

def every_tick(api: API):
    update(api)

    if info.stage == StageClass.START:
        stage_start(api)
        print(f"team {info.team_id} is on stage START")
        info.stage = StageClass.EXPLORE
        # api.send_chat('開始')

    if info.stage == StageClass.EXPLORE:
        print(f"team {info.team_id} is on stage EXPLORE")
        stage_explore(api)
        # api.send_chat('探索')

        # 找到塔後，向塔攻擊
        if info.target_tower is not None:
            info.stage = StageClass.ATTACK_TOWER

    elif info.stage == StageClass.ATTACK_TOWER:
        print(f"team {info.team_id} is on stage ATTACK_TOWER")
        stage_attack_tower(api)
        # api.send_chat('攻塔')

        # 打下塔了，開始守塔
        if info.target_tower.team_id == info.team_id:
            info.defend_tower = info.target_tower
            info.target_tower = None
            info.stage = StageClass.DEFENCE_TOWER

        elif info.defend_tower is not None and info.defend_tower.team_id != api.get_team_id() and info.defend_tower.team_id != 0:
            info.target_tower = info.defend_tower
            info.stage = StageClass.ATTACK_ENEMY_TOWER
        
    elif info.stage == StageClass.DEFENCE_TOWER:
        print(f"team {info.team_id} is on stage DEFENCE_TOWER")
        stage_defend_tower(api)
        # api.send_chat('守塔')

        # 塔被人打下了，打回來！
        if info.defend_tower is not None and info.defend_tower.team_id != api.get_team_id() and info.defend_tower.team_id is not 0:
            info.target_tower = info.defend_tower
            info.stage = StageClass.ATTACK_ENEMY_TOWER
        if len(api.get_owned_characters()) > 20 and info.defend_tower.health > 500:
            info.stage = StageClass.TOWER_ATTACK_ENEMY

    elif info.stage == StageClass.TOWER_ATTACK_ENEMY:
        print(f"team {info.team_id} is on stage TOWER_ATTACK_ENEMY")
        stage_tower_attack_enemy(api)
        # api.send_chat('游擊')
        if len(api.get_owned_characters()) < 15:
            info.stage = StageClass.DEFENCE_TOWER
        elif info.target_enemy is None:
            info.stage = StageClass.EXPLORE
        elif len(api.get_owned_towers()) < 2:
            info.stage = StageClass.ATTACK_ENEMY_TOWER
        elif info.defend_tower.health <= 500:
            info.stage = StageClass.DEFENCE_TOWER
        

    elif info.stage == StageClass.ATTACK_ENEMY_TOWER:
        print(f"team {info.team_id} is on stage ATTACK_ENEMY_TOWER")
        stage_attack_enemy_tower(api)
        if len(api.get_owned_towers()) >= 2:
            info.stage = StageClass.DEFENCE_TOWER
        
    else:
        print("wrong stage")
        info.stage = StageClass.EXPLORE

    # 設定所有人都會攻擊某一個目標，邊走邊攻擊！
    for character in api.get_owned_characters():
        enemy = api.within_attacking_range(character)
        if len(enemy) != 0:
            api.action_attack(character, random.choice(enemy))
    print(info.target_enemy)
    
    # print(novel[novel_count], novel_count)
    api.send_chat(info.novel[int(api.get_current_time()) % len(info.novel)])