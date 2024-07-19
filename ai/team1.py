"""
sample3 的精進版本
"""
import math
import random
 
import pygame as pg
 
from api.prototype import *
 
starting_amount = 0
 
 
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
 
MELEE_list=[]

leaved = dict()

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
 
    # ATTACK_ENEMY = auto()
    # """攻擊敵人階段"""
 
 
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
    """
    探索地圖階段，會讓所有的士兵在地圖上亂走。
    """
    # 讓所有的塔生成近戰士兵（近戰士兵的生成機率為1）
    change_spawn_by_posibility(api, api.get_owned_towers(), 1, 0, 0)
    for character in api.get_owned_characters():
        api.action_wander(character)
 
    # 如果找到不屬於自己的中立塔，就從中選一個離主堡（fountain）最近的存起來
    others_towers = [tower for tower in api.get_visible_towers() if not tower.is_fountain and tower.team_id != info.team_id]
    if len(others_towers) != 0:
        info.target_tower = api.sort_by_distance(others_towers, info.fountain.position)[0]
 
 
def stage_attack_tower(api: API):
    """
    攻擊塔階段，會讓所有的士兵都去往某個塔走，進行攻擊。
    """
    # 改變所有塔生成的兵種，讓我們更容易打下塔！
    change_spawn_by_posibility(api, api.get_owned_towers(), 0.6, 0.4, 0)
 
    # 攻擊塔
    my_characters = api.get_owned_characters()
    all_characters = api.get_visible_characters()
    if info.target_tower.health > 1000:
        enemies = []
        enemies_inside_tower = []
        for character in all_characters:
            if character.team_id != api.get_team_id():
                enemies.append(character)
            if character.position.distance_to(info.target_tower.position) < 30:
                enemies_inside_tower.append(character)
        for character in my_characters:
            if info.target_tower.position.distance_to(character.position) < 55 and len(enemies_inside_tower)!=0 and (character.id,info.target_tower.id) in leaved and leaved[(character.id,info.target_tower.id)] == 1:
                if info.target_tower.position.distance_to(character.position) < 45:
                    api.action_move_along(character, character.position - info.target_tower.position)
                    if (character.id,info.target_tower.id) not in leaved:  
                        leaved[(character.id,info.target_tower.id)] = 0
                else:
                    api.action_move_clear(character)
                api.action_cast_ability(character)
                nearest_enemy = api.sort_by_distance(enemies, character.position)[0]
                api.action_attack(character, nearest_enemy)
            else:
                if (character.id,info.target_tower.id) in leaved and leaved[(character.id,info.target_tower.id)] == 0:  
                    leaved[(character.id,info.target_tower.id)] = 1
                api.action_move_to(character, info.target_tower.position)
                api.action_cast_ability(character)
                api.action_attack(character, info.target_tower)
    else:
        api.action_move_to(api.get_owned_characters(), info.target_tower.position)
        api.action_cast_ability(api.get_owned_characters())
        api.action_attack(api.get_owned_characters(), info.target_tower)
 
 
def stage_defend_tower(api: API):
    """
    防禦塔階段，會讓所有的士兵都往某個塔走。
    """
    # 改變塔生成的兵種，讓我們更容易把塔守好！
    for tower in api.get_owned_towers():
        if tower.is_fountain:
            change_spawn_by_posibility(api, [tower], 1, 0, 0)
        else:
            change_spawn_by_posibility(api, [tower], 0.4, 0, 0.6)
 
    # 往我們要守的塔移動！
    api.action_move_to(api.get_owned_characters(), info.defend_tower.position)
 
# def stage_attack_enemy(api: API):
#     """
#     攻擊其他人的階段，會讓所有的士兵都往某個敵對士兵走。
#     """
#     # 如果已經有要攻擊的士兵了
#     pass
 
 
info = AiInfo()
 
def every_tick(api: API):
    """
    一定要被實作的 function ，會定期被遊戲 call
    在使用 VS Code 寫 code 的時候可以把滑鼠移到變數、函數上方，看它們的詳細解說。
    在使用 VS Code 寫 code 的時候可以按住 Ctrl 再用滑鼠點擊變數、函數，來跳轉到與它們相關的地方。
    在測試的時候可以只放一隻 ai 、在執行時一次加很多 arguments (如 -qrp)。
    """
    global MELEE_list
    global starting_amount
 
    if starting_amount < 12:
 
        # 將生成的兵種都換成 MELEE
        my_towers=api.get_owned_towers()
        for tower in my_towers:
            if tower.spawn_character_type is not CharacterClass.MELEE:
                api.change_spawn_type(tower, CharacterClass.MELEE)
 
        
 
        """
        # 更新所有 MELEE_list 裡面的士兵的參數
        MELEE_list = [api.refresh_character(i) for i in MELEE_list]
        for i in my_characters:
            if i.type == CharacterClass.MELEE and len(MELEE_list) < 9 and i not in MELEE_list:
                MELEE_list.append(i)
        """
        my_characters=api.get_owned_characters()
        current_characters_amount = len(my_characters)
        
        destinations = [[240,5], [240,75], [240,174], [174,240], [75,240], [10,240]]
        number=[1,2,3,4,5,6,7,8,9,10]
        if current_characters_amount >= starting_amount+1 and my_characters[starting_amount] is not None:
            # print(f'{starting_amount}{starting_amount}{starting_amount}')
            api.action_wander(my_characters)
            api.action_cast_ability(my_characters)  # 不管三七二十一把技能打開
            starting_amount += 1  
    else:
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