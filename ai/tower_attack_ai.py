"""
Author: CppNoPointer
AI 原理：
目前 AI 會將戰鬥分成三個階段：
1. 探視野階段：
從溫泉生成近戰兵，並使每個近戰兵隨機探索未探索的點區域，直到找到一座中立塔
2. 攻略中立塔階段：
切換生成遠程兵，如果現在派遣在外的兵超過 5 個，便從溫泉派出軍隊將中立塔拿下
否則將兵召集回溫泉，如果召集的兵力超過 10 個，便再次派遣
若攻下中立塔，並進入下一階段
3. 對戰階段：
召集所有軍隊攻擊第一個非友軍單位
"""


import math
import random

import pygame as pg

from api.prototype import *

last_point = pg.Vector2(0, 0)

def get_fountain(visible_towers, my_team_id):
    for tower in visible_towers:
        if tower.is_fountain and my_team_id == tower.team_id:
            return tower


def every_tick(api: API):
    scores = []

    for team_id in range(0, 4):
        scores.append(api.get_score_of_team(team_id))

    # print(scores)
    
    print(scores)

    my_team_id = api.get_team_id()


    owned_characters = api.get_owned_characters()
    visible_towers = api.get_visible_towers()
    owned_characters_count = len(owned_characters)
    visible_towers_count = len(visible_towers)
    fountain = get_fountain(visible_towers, my_team_id)
    #print(visible_towers, fountain)

    recruited_characters = []
    dispatched_characters = []
    owned_tower = api.get_owned_towers()
    for character in owned_characters:
        recruited = False
        for tower in owned_tower:
            if character.position.distance_to(tower.position) <= 50:
                recruited = True
                break
        if recruited: recruited_characters.append(character)
        else: dispatched_characters.append(character)
    recruited_characters_count = len(recruited_characters)
    dispatched_characters_count = len(dispatched_characters)
    

    if (visible_towers_count <= 1):
        api.change_spawn_type(fountain, CharacterClass.MELEE)
        
        if (recruited_characters_count >= 1):
            random_point = None
            while True:
                random_point = pg.Vector2(random.random() * 250, random.random() * 250)
                if not api.is_visible(random_point):
                    break
            #print(random_point)
            #api.action_move_along(owned_characters[:], direction)
            for index in range(len(recruited_characters)):
                if api.get_movement(recruited_characters[index]).status == MovementStatusClass.STOPPED:
                    api.action_move_to(recruited_characters[index:(index + 1)], random_point)
    else: 
        target_tower = None
        for tower in visible_towers:
            if not tower.is_fountain and tower.team_id != my_team_id:
                target_tower = tower
                break
        if target_tower != None:
            api.change_spawn_type(fountain, CharacterClass.RANGER)
            #print(recruited_characters_count, dispatched_characters_count)
            if dispatched_characters_count <= 5 and dispatched_characters_count != 0: 
                api.action_move_to(dispatched_characters[:],
                                        fountain.position)
            elif owned_characters_count >= 10:
                if dispatched_characters_count != 0:
                    api.action_move_to(dispatched_characters, target_tower.position)
                    api.action_attack(dispatched_characters, target_tower)
                else:
                    api.action_move_along(owned_characters, pg.Vector2(1, 1))
        else: 
            
            for tower in owned_tower:
                api.change_spawn_type(tower, CharacterClass.RANGER)
            visible_enemy = [character for character in api.get_visible_characters()
                if character.team_id != my_team_id]
            
            if len(visible_enemy):
                api.action_move_to(owned_characters[:], visible_enemy[0].position)
                api.action_cast_ability(owned_characters[:])
                api.action_attack(owned_characters[:], visible_enemy[0])

