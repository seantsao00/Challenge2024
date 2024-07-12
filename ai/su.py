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


def every_tick(api: API):
    scores = []
    
    for team_id in range(0, 4):
        scores.append(api.get_score_of_team(team_id))

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

    stopped_characters = []
    moving_characters = []
    for character in owned_characters:
        if api.get_movement(character).status == MovementStatusClass.STOPPED:
            stopped_characters.append(character)
        else:
            moving_characters.append(character)
    stopped_characters_count = len(stopped_characters)
    moving_characters_count = len(moving_characters)
    

    if (visible_towers_count <= 1):
        if (owned_characters_count <= 15):
            api.change_spawn_type(fountain, CharacterClass.MELEE)
            random_point = pg.Vector2(random.random() * 250, random.random() * 250)
            api.action_move_to(owned_characters, random_point)
        else:
            api.change_spawn_type(fountain, CharacterClass.RANGER)
            owned_ranger = [ranger for ranger in owned_characters if ranger.type == CharacterClass.RANGER]
            api.action_move_clear(owned_ranger)
        
        if (stopped_characters_count >= 1):
            random_point = pg.Vector2(random.random() * 250, random.random() * 250)
            api.action_move_to(owned_characters, random_point)      
        
    else: 
        target_tower = None
        for tower in visible_towers:
            if not tower.is_fountain and tower.team_id != my_team_id:
                target_tower = tower
                break
        if target_tower != None:
            api.change_spawn_type(fountain, CharacterClass.RANGER)
            if moving_characters_count <= 10 and moving_characters_count != 0: 
                api.action_move_to(moving_characters[:],
                                        fountain.position)
            elif owned_characters_count >= 20:
                if moving_characters_count != 0:
                    api.action_move_to(moving_characters, target_tower.position)
                    api.action_attack(moving_characters, target_tower)
                else:
                    api.action_move_along(owned_characters, pg.Vector2(1, 1))
        else: 
            owned_tower = api.get_owned_towers()
            
            for tower in owned_tower:
                if not tower.is_fountain: api.change_spawn_type(tower, CharacterClass.RANGER)
                else: api.change_spawn_type(tower, CharacterClass.RANGER)
            
            if enemy_count:
                enemy_sniper = [sniper for sniper in owned_characters if sniper.type == CharacterClass.SNIPER]
                api.action_move_to(owned_characters[:], visible_enemy[0].position)
                api.action_cast_ability(owned_characters[:])
                if (len(enemy_sniper) > 0):
                    api.action_attack(owned_characters[:], enemy_sniper[0])
                api.action_attack(owned_characters[:], visible_enemy[0])

