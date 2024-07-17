"""
sample3 的精進版本
"""
import math
import random

import pygame as pg

from api.prototype import *


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


def every_tick(api: API):
    """
    一定要被實作的 function ，會定期被遊戲 call
    在使用 VS Code 寫 code 的時候可以把滑鼠移到變數、函數上方，看它們的詳細解說。
    在使用 VS Code 寫 code 的時候可以按住 Ctrl 再用滑鼠點擊變數、函數，來跳轉到與它們相關的地方。
    在測試的時候可以只放一隻 ai 、在執行時一次加很多 arguments (如 -qrp)。
    """
    my_towers = api.get_owned_towers()
    for tower in my_towers:
        if tower.spawn_character_type is not CharacterClass.MELEE:
            # 把塔所生的士兵種類改成近戰，因為近戰走得比較快
            api.change_spawn_type(tower, CharacterClass.MELEE)
    my_characters = api.get_owned_characters()
    api.action_cast_ability(my_characters)  # 不管三七二十一把技能打開
    for character in my_characters:  # 用 for 迴圈遍歷所有自己的士兵
        if api.get_movement(character).status is MovementStatusClass.STOPPED:  # 這個士兵停止移動了
            stick = random.random()  # 抽個籤
            if stick < 0.5:  # 讓角色去探索沒有視野的地方
                assign_random_destination(character, api)
            else:  # 讓角色開始隨意亂走
                api.action_wander(character)
