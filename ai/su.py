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

def handle_attack(api: API):
    api.send_chat(random.choice(["鄭詠堯說你是2486"]))

def handle_spawn(api: API):
    api.send_chat(random.choice(["鄭詠堯說你是2486"]))

def init(api: API):
    api.send_chat(random.choice(["鄭詠堯說你是2486"]))

def send_spam_message(api: API):
    api.send_chat(random.choice(["鄭詠堯說你是2486"]))

class Strategy:
    def __init__(self):
        self.api: API | None = None
        self.fountain: Tower = None
        self.owned_towers: list[Tower] = []
        self.my_team_id: int = None
        
        self.owned_characters: list[Character] = []
        self.detective_team: list[Character] = []
        
        self.visible_enemy: list[Character] = []
        self.visible_enemy_towers: list[Tower] = []
        
        self.cnt: int = 0
        
    def initialize(self):
        self.my_team_id = self.api.get_team_id()
        self.fountain = self.get_fountain(self.api.get_visible_towers(), self.my_team_id)
        self.owned_characters = self.api.get_owned_characters()
        
        self.visible_enemy = [character for character in self.api.get_visible_characters()
        if character.team_id != self.my_team_id]
        self.visible_enemy_towers = [tower for tower in self.api.get_visible_towers() if 
                                     tower.team_id != self.my_team_id]
        
        
        self.cnt += 1

        
    def send_spam_message(self):
        self.api.send_chat(random.choice(["鄭詠堯說你是2486"]))
    def print_scores(self):
        scores = []
        for team_id in range(0, 4):
            scores.append(self.api.get_score_of_team(team_id))
        print(scores)
        
    def get_fountain(self, visible_towers: list[Tower], my_team_id: int):
        for tower in visible_towers:
            if tower.is_fountain and my_team_id == tower.team_id:
                return tower
        
    def handle_spawn(self):
        if (len(self.owned_characters) <= 5 and len(self.api.get_visible_towers()) <= 1):
            self.api.change_spawn_type(self.fountain, CharacterClass.MELEE)
        else:
            self.api.change_spawn_type(self.fountain, CharacterClass.RANGER)
        
        # raise NotImplementedError
        
    def attack_target(self, target: Character | Tower):
        self.api.action_move_to(self.owned_characters, target.position)
        self.api.action_attack(self.owned_characters, target)
        self.api.action_cast_ability(self.owned_characters, position = target.position)
    
        
    def handle_attack(self):
        
        if (len(self.api.get_owned_towers()) <= 1):
            self.api.action_wander(self.owned_characters)
            
            if (len(self.visible_enemy) > 0):
                self.attack_target(self.visible_enemy[0])

        else:
            if (len(self.owned_characters) < 15 and len(self.owned_towers) <= 1):
                if (len(self.owned_characters) > len(self.visible_enemy) and len(self.visible_enemy) > 0):
                    self.attack_target(self.visible_enemy[0])
                else:
                    self.api.action_move_to(self.owned_characters[:], pg.Vector2(20, 20))
                
            elif (len(self.visible_enemy) > 0 and len(self.owned_characters) - len(self.visible_enemy) > 15):
                self.attack_target(self.visible_enemy[0])
            else:                
                if (len(self.visible_enemy_towers) > 0):
                    self.attack_target(self.visible_enemy_towers[0])
                else:
                    self.api.action_wander(self.owned_characters)
                
                
        
        # raise NotImplementedError
        
    def run(self, api: API):
        self.api = api
        self.send_spam_message()
        self.print_scores()
        
        self.initialize()
        
        self.handle_spawn()
        self.handle_attack()
        
        
strategy = Strategy()

def every_tick(api: API):
    
    strategy.run(api)