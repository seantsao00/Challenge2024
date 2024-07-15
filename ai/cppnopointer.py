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

def assign_random_destination(character: Character, interface: API):
    """assign 一個還沒有開視野的 random position 給 character 。"""
    new_destination = pg.Vector2(random.uniform(0, interface.get_grid_size() - 1),
                                 random.uniform(0, interface.get_grid_size() - 1))
    i = 0
    while interface.is_visible(new_destination):
        new_destination = pg.Vector2(random.uniform(0, interface.get_grid_size() - 1),
                                     random.uniform(0, interface.get_grid_size() - 1))
        i += 1
        if i == 10: # 最多嘗試 10 次
            break
    interface.action_move_to([character], new_destination)

def move_and_attack(characters, visible_enemy, owned_tower, no_sniper_characters, api):
    index = -1
    
    defend = False
    defend_tower = None
    for tower in owned_tower:
        if tower.is_fountain: continue
        if len(enemies_near_tower(visible_enemy, tower, api)) > 0:
            defend = True
            defend_tower = tower
            break
    
    
    if defend:
        api.action_move_to(no_sniper_characters, defend_tower.position)
    elif len(visible_enemy) == 0:
        api.action_wander(no_sniper_characters)
    else:
        api.action_move_to(no_sniper_characters, visible_enemy[0].position)
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
            if (len(visible_enemy) != 0): api.action_attack(characters[index:index + 1], visible_enemy[0])
            continue
        else:
            random_target = random.choice(attackable)
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

def snipers_defending_tower(tower, api):
    return [character for character in api.get_visible_characters()
                if character.team_id == api.get_team_id() and character.type == CharacterClass.SNIPER and character.position.distance_to(tower.position) <= 40]

def every_tick(api: API):
    
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
        if recruited: recruited_characters.append(character)
        elif character.type != CharacterClass.SNIPER: dispatched_characters.append(character)
    recruited_characters_count = len(recruited_characters)
    dispatched_characters_count = len(dispatched_characters)
    contestable_tower = []
    for tower in visible_towers:
        if not tower.is_fountain:
            contestable_tower.append(tower)
    contestable_tower_count = len(contestable_tower)
    print(owned_characters_count, recruited_characters_count, dispatched_characters_count)
    api.action_cast_ability(owned_characters[:])
    no_sniper_characters = []
    sniper_characters = []

    for character in owned_characters:
        if character.type != CharacterClass.SNIPER:
            no_sniper_characters.append(character)
        else:
            sniper_characters.append(character)
    
    target_tower = None
    if (len(contestable_tower) == 0):
        if (len(no_sniper_characters) >= 10): api.change_spawn_type(fountain, random.choice([CharacterClass.MELEE, CharacterClass.SNIPER]))
        else: api.change_spawn_type(fountain, random.choice([CharacterClass.MELEE]))
        
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
            for character in owned_characters:
                attackable = api.within_attacking_range(character)
                if len(attackable) > 0: 
                    random_target = random.choice(attackable)
                    api.action_cast_ability([character])
                    api.action_attack([character], random_target)
    else: 
        
        for tower in visible_towers:
            if not tower.is_fountain and tower.team_id != my_team_id:
                if (target_tower != None and len(enemies_near_tower(visible_enemy, tower, api)) < len(enemies_near_tower(visible_enemy, target_tower, api))) or target_tower == None:
                    target_tower = tower
        for tower in owned_tower:
            if (tower.is_fountain): 
                if len(snipers_defending_tower(fountain, api)) >= 4: 
                    print("Sniper defending fountain:" + str(len(snipers_defending_tower(fountain, api))))
                    api.change_spawn_type(fountain, random.choice([CharacterClass.MELEE, CharacterClass.RANGER]))
                else: api.change_spawn_type(fountain, random.choice([CharacterClass.MELEE, CharacterClass.RANGER, CharacterClass.SNIPER]))
            else: 
                print("Sniper defending tower:" + str(len(snipers_defending_tower(tower, api))))
                if (len(snipers_defending_tower(tower, api)) < 5): api.change_spawn_type(tower, random.choice([CharacterClass.SNIPER]))
                else: api.change_spawn_type(tower, random.choice([CharacterClass.MELEE, CharacterClass.RANGER]))
        if target_tower != None:
            
            #print(recruited_characters_count, dispatched_characters_count)
            if dispatched_characters_count <= 5 and dispatched_characters_count != 0: 
                occupied_tower = []
                for tower in owned_tower:
                    if not tower.is_fountain: occupied_tower.append(tower)
                if (len(occupied_tower) > 0): api.action_move_to(dispatched_characters + recruited_characters, occupied_tower[0].position)
                else: api.action_move_to(dispatched_characters + recruited_characters, fountain.position)
                for character in owned_characters:
                    attackable = api.within_attacking_range(character)
                    if len(attackable) > 0: 
                        random_target = random.choice(attackable)
                        api.action_cast_ability([character])
                        api.action_attack([character], random_target)
                
            elif dispatched_characters_count + recruited_characters_count >= 10 or dispatched_characters_count >= 5:
                
                if dispatched_characters_count != 0:
                    api.action_move_to(no_sniper_characters, target_tower.position)
                    api.action_attack(no_sniper_characters, target_tower)
                    api.action_cast_ability(no_sniper_characters)
                    
                    #attack(dispatched_characters, api)
                else:
                    api.action_move_along(no_sniper_characters, pg.Vector2(1, 1))
            
        else: 
            
            if dispatched_characters_count >= 5 or (recruited_characters_count >= 10):
            
                #api.action_move_to(owned_characters[:], visible_enemy[0].position)
                
                #api.action_attack(owned_characters[:], visible_enemy[0])
                move_and_attack(owned_characters, visible_enemy, owned_tower, no_sniper_characters, api)
            else:
                occupied_tower = []
                for tower in owned_tower:
                    if not tower.is_fountain: occupied_tower.append(tower)
                if (len(occupied_tower) > 0): api.action_move_to(dispatched_characters + recruited_characters, occupied_tower[0].position)
                else: api.action_move_to(dispatched_characters + recruited_characters, fountain.position)
    for sniper in sniper_characters:
        nearest_distance = 1e9
        for tower in contestable_tower:
            if tower.team_id == my_team_id: continue
            nearest_distance = min(nearest_distance, tower.position.distance_to(sniper.position))
        if len(api.within_attacking_range(sniper)) > 0: 
            api.action_move_clear([sniper])
            enemy_rangers = []
            for target_enemy in api.within_attacking_range(sniper):
                if type(target_enemy) != Tower and target_enemy.type == CharacterClass.RANGER: enemy_rangers.append(target_enemy)
            if len(enemy_rangers) > 0: api.action_attack([sniper], random.choice(enemy_rangers))
            else: api.action_attack([sniper], random.choice(api.within_attacking_range(sniper)))
            
        elif nearest_distance <= 60:
            api.action_move_clear([sniper])
        elif (target_tower != None): api.action_move_to([sniper], target_tower.position)
        else: api.action_wander([sniper])