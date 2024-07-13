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

def send_spam_message(api: API):
    api.send_chat(random.choice(["😔😔😔😔😔",
                                       "鄭詠堯說你是2486",
                                       "\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17",
                                       "哥們，這條刪了唄，我是無所謂的，沒那麼容易破防的，真的，我不輕易破防，但是我一個朋友可能有點汗流浹背了，他不太舒服想睡了，當然不是我哈，我一直都是行的，以一個旁觀者的心態看吧，也不至於破防吧，就是想照顧下我朋友的感受，他有點破防了，還是建議刪了吧，當然刪不刪隨你，我是沒感覺的，就是為朋友感到不平罷了，也不是那麼輕易破防的，求你了，刪了唄"]))


def every_tick(api: API):
    send_spam_message(api)
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
    
    stopped_characters = []
    moving_characters = []
    for character in owned_characters:
        if api.get_movement(character).status == MovementStatusClass.STOPPED:
            stopped_characters.append(character)
        else:
            moving_characters.append(character)
    stopped_characters_count = len(stopped_characters)
    moving_characters_count = len(moving_characters)    
    
    print(stopped_characters_count)
    if (visible_towers_count <= 1 and owned_characters_count > 0):
        if (owned_characters_count <= 15):
            api.change_spawn_type(fountain, CharacterClass.RANGER)

            api.action_wander(owned_characters)
        else:
            api.change_spawn_type(fountain, CharacterClass.RANGER)
            owned_ranger = [ranger for ranger in owned_characters if ranger.type == CharacterClass.RANGER]
            random_point = pg.Vector2(random.random() * 250, random.random() * 250)
            api.action_move_to(owned_ranger, random_point)
            
            
        if enemy_count:
            target_enemy = attack_nearest_enemy(api, owned_characters, visible_enemy)
            api.action_move_to(owned_characters[:], visible_enemy[target_enemy].position)
            api.action_cast_ability(owned_characters[:], position = visible_enemy[target_enemy].position)
        else:
            owned_ranger = [ranger for ranger in owned_characters if ranger.type == CharacterClass.RANGER]
            random_point = pg.Vector2(random.random() * 250, random.random() * 250)
            api.action_move_to(owned_ranger, random_point)  
            
    else: 
        target_tower = None
        for tower in visible_towers:
            if not tower.is_fountain and tower.team_id != my_team_id:
                target_tower = tower
                break
        if target_tower != None:
            api.change_spawn_type(fountain, CharacterClass.RANGER)
                    
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