"""
Author: CppNoPointer
AI 原理：
目前 AI 會將戰鬥分成三個階段：
1. 探視野階段：
從溫泉生成近戰兵，並使每個近戰兵隨機探索未探索的點區域，直到找到一座中立塔
2. 攻略中立塔階段：
切換生成狙擊兵，如果現在派遣在外的兵超過 5 個，便從溫泉派出軍隊將中立塔拿下
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

def move_and_attack(characters, visible_enemy, api):
    index = -1
    for character in characters:
        index += 1
        attackable = api.within_attacking_range(character)
        #print(index, attackable)
        #print(visible_enemy)
        if (len(attackable) == 0): 
            if (character.type != CharacterClass.SNIPER):
                if (len(visible_enemy) == 0):
                    print("no enemies seen")
                    api.action_wander(characters[index:index + 1])
                else: api.action_move_to(characters[index:index + 1], visible_enemy[0].position)
            if (len(visible_enemy) != 0): api.action_attack(characters[index:index + 1], visible_enemy[0])
            continue
        random_target = random.choice(attackable)
        if (character.type != CharacterClass.SNIPER): api.action_move_to(characters[index:index + 1], random_target.position)
        api.action_attack(characters[index:index + 1], random_target)
        
def enemies_near_tower(visible_enemies, tower, api):
    ret = []
    for enemy in visible_enemies:
        if enemy.position.distance_to(tower.position) <= 20:
            ret.append(enemy)
    return ret

def get_fountain(visible_towers, my_team_id):
    for tower in visible_towers:
        if tower.is_fountain and my_team_id == tower.team_id:
            return tower


def every_tick(api: API):
    print(f"hao's team is {api.get_team_id()}")
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
    visible_enemy = [character for character in api.get_visible_characters()
                if character.team_id != my_team_id]
    owned_tower = api.get_owned_towers()
    for character in owned_characters:
        recruited = False
        for tower in owned_tower:
            if character.position.distance_to(tower.position) <= 20 and api.get_movement(character).status == MovementStatusClass.STOPPED:
                recruited = True
                break
        if recruited and character.type != CharacterClass.SNIPER: recruited_characters.append(character)
        elif not recruited: dispatched_characters.append(character)
    recruited_characters_count = len(recruited_characters)
    dispatched_characters_count = len(dispatched_characters)
    contestable_tower = []
    for tower in visible_towers:
        if not tower.is_fountain:
            contestable_tower.append(tower)
    contestable_tower_count = len(contestable_tower)
    print(owned_characters_count, recruited_characters_count, dispatched_characters_count)
    if (contestable_tower_count == 0):
        api.change_spawn_type(fountain, random.choice([CharacterClass.MELEE]))
        
        if (recruited_characters_count >= 1):
            random_point = None
            while True:
                random_point = pg.Vector2(random.random() * 250, random.random() * 250)
                if not api.is_visible(random_point):
                    break
            #print(random_point)
            #api.action_move_along(owned_characters[:], direction)
            """
            for index in range(len(recruited_characters)):
                if api.get_movement(recruited_characters[index]).status == MovementStatusClass.STOPPED:
                    api.action_move_to(recruited_characters[index:(index + 1)], random_point)
            """
            api.action_wander(owned_characters)
    else: 
        target_tower = None
        
        for tower in visible_towers:
            if not tower.is_fountain and tower.team_id != my_team_id:
                target_tower = tower
                break
        if target_tower != None:
            api.change_spawn_type(fountain, random.choice([CharacterClass.MELEE, CharacterClass.RANGER]))
            #print(recruited_characters_count, dispatched_characters_count)
            if dispatched_characters_count <= 5 and dispatched_characters_count != 0: 
                api.action_move_to(dispatched_characters[:],
                                        fountain.position)
                
                
            elif owned_characters_count >= 10:
                no_sniper_characters = []
                for character in owned_characters:
                    if character.type != CharacterClass.SNIPER:
                        no_sniper_characters.append(character)
                if dispatched_characters_count != 0:
                    if len(enemies_near_tower(visible_enemy, target_tower, api)) > 0:
                        target_enemy = random.choice(enemies_near_tower(visible_enemy, target_tower, api))
                        api.action_move_to(no_sniper_characters, target_enemy.position)
                        api.action_attack(no_sniper_characters, target_enemy)
                    else:
                        api.action_move_to(no_sniper_characters, target_tower.position)
                        api.action_attack(no_sniper_characters, target_tower)
                    api.action_cast_ability(no_sniper_characters)
                    
                    #attack(dispatched_characters, api)
                else:
                    api.action_move_along(no_sniper_characters, pg.Vector2(1, 1))
        else: 
            
            for tower in owned_tower:
                if (tower.is_fountain): api.change_spawn_type(tower, random.choice([CharacterClass.RANGER, CharacterClass.MELEE]))
                else: api.change_spawn_type(tower, random.choice([CharacterClass.SNIPER]))
            
            
            
            #api.action_move_to(owned_characters[:], visible_enemy[0].position)
            api.action_cast_ability(owned_characters[:])
            #api.action_attack(owned_characters[:], visible_enemy[0])
            move_and_attack(owned_characters, visible_enemy, api)

