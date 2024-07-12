"""
Author: Su
AI 原理：
目前 AI 會將戰鬥分成三個階段：
1. 探視野階段：
2. 攻略中立塔階段：
3. 對戰階段：
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

def attack_nearest_enemy(api: API,owned_characters: list[Character], visible_enemy: list[Character]):
    cnt = 0
    res = 0
    min_dist = 1e6
    for enermies in visible_enemy:
        now_dist = owned_characters[0].position.distance_to(enermies.position)
        if (now_dist < min_dist):
            res = cnt
            min_dist = now_dist
        cnt += 1
    
    return res


def every_tick(api: API):
    scores = []
    
    for team_id in range(0, 4):
        scores.append(api.get_score_of_team(team_id))

    print(f"su's team is {api.get_team_id()}")
    print(scores)

    my_team_id = api.get_team_id()

    owned_characters = api.get_owned_characters()
    visible_enemy = [character for character in api.get_visible_characters()
    if character.team_id != my_team_id]
    
    visible_towers = api.get_visible_towers()
    owned_characters_count = len(owned_characters)
    visible_towers_count = len(visible_towers)
    enemy_count = len(visible_enemy)

    fountain = get_fountain(visible_towers, my_team_id)
    

    if (visible_towers_count <= 1 and owned_characters_count > 0):
        if (owned_characters_count <= 15):
            api.change_spawn_type(fountain, CharacterClass.RANGER)

            api.action_wander(owned_characters)
        else:
            api.change_spawn_type(fountain, CharacterClass.RANGER)
            owned_ranger = [ranger for ranger in owned_characters if ranger.type == CharacterClass.RANGER]
            random_point = pg.Vector2(random.random() * 125, random.random() * 125)
            api.action_move_to(owned_ranger, random_point)
           
            
        if enemy_count:
            target_enemy = attack_nearest_enemy(api, owned_characters, visible_enemy)
            api.action_move_to(owned_characters[:], visible_enemy[target_enemy].position)
            api.action_cast_ability(owned_characters[:], position = visible_enemy[target_enemy].position)
    else: 
        target_tower = None
        for tower in visible_towers:
            if not tower.is_fountain and tower.team_id != my_team_id:
                target_tower = tower
                break
        if target_tower != None:
            api.change_spawn_type(fountain, CharacterClass.RANGER)
            # if moving_characters_count <= 10 and moving_characters_count != 0: 
            #     api.action_move_to(moving_characters[:],
            #                             fountain.position)
            # elif owned_characters_count >= 20:
                    
            if enemy_count:
                target_enemy = attack_nearest_enemy(api, owned_characters, visible_enemy)
                api.action_move_to(owned_characters[:], visible_enemy[target_enemy].position)
                api.action_cast_ability(owned_characters[:], position = visible_enemy[target_enemy].position)

        else: 
            owned_tower = api.get_owned_towers()
            
            for tower in owned_tower:
                if not tower.is_fountain: api.change_spawn_type(tower, CharacterClass.RANGER)
                else: api.change_spawn_type(tower, CharacterClass.RANGER)
            
            if enemy_count:
                target_enemy = attack_nearest_enemy(api, owned_characters, visible_enemy)
                api.action_move_to(owned_characters[:], visible_enemy[target_enemy].position)
                api.action_cast_ability(owned_characters[:], position = visible_enemy[target_enemy].position)
            else:
                api.action_move_to(owned_characters[:], (250,0))