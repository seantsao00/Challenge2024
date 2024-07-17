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
        
    def initialize(self):
        self.my_team_id = self.api.get_team_id()
        self.fountain = self.get_fountain(self.api.get_visible_towers(), self.my_team_id)
        self.owned_characters = self.api.get_owned_characters()
        
        self.visible_enemy = [character for character in self.api.get_visible_characters()
        if character.team_id != self.my_team_id]
        self.visible_enemy_towers = [tower for tower in self.api.get_visible_towers() if 
                                     tower.team_id != self.my_team_id]
        
    def send_spam_message(self):
        scores = []
        for team_id in range(1, 5):
            scores.append(self.api.get_score_of_team(team_id))
            
        if (self.api.get_score_of_team(self.my_team_id) == min(scores)):
            self.api.send_chat(random.choice(["喜歡你的第一年我還沒有告白"]))  
                 
        elif (self.api.get_score_of_team(self.my_team_id) == max(scores)):
            self.api.send_chat(random.choice(["我只能永遠讀著對白，讀著我給你的傷害", "發動精神攻擊", "家人們點個讚", "素質真高"]))
        else:
            self.api.send_chat(random.choice(["未必，確實，這我", "5/21網路二一節 我依然堅守本群 未曾離開 沒有寫作業",
                                              "沒了你的生活變得 很枯燥😕 像是皮卡丘 他很浮躁🤬"]))
        
    def print_scores(self):
        scores = []
        for team_id in range(1, 5):
            print(team_id)
            scores.append(self.api.get_score_of_team(team_id))
        print(scores)
        
    def get_fountain(self, visible_towers: list[Tower], my_team_id: int):
        for tower in visible_towers:
            if tower.is_fountain and my_team_id == tower.team_id:
                return tower
        
    def handle_spawn(self):
        if (len(self.owned_characters) <= 4 and len(self.api.get_visible_towers()) <= 1):
            self.api.change_spawn_type(self.fountain, CharacterClass.MELEE)
        else:
            self.api.change_spawn_type(self.fountain, CharacterClass.SNIPER)
            
        if (len(self.visible_enemy_towers) > 0):
            self.api.change_spawn_type(self.fountain, CharacterClass.SNIPER)
        
        # raise NotImplementedError
        
    def effective_attack(self):
        for character in self.owned_characters:
            attackable = self.api.within_attacking_range(character)
            if (len(attackable) > 0):
                
                attackable_sniper = [snipers for snipers in attackable if type(snipers) == Character 
                                    and (snipers.type == CharacterClass.SNIPER)]
                attackable_ranger = [rangers for rangers in attackable if type(rangers) == Character 
                                    and (rangers.type == CharacterClass.RANGER)]
                
                attackable_tower = [tower for tower in attackable if type(tower) == Tower and not tower.is_fountain]
                near_tower = [near_towers for near_towers in self.visible_enemy_towers if near_towers.health < 500 and not near_towers.is_fountain 
                              and near_towers.position.distance_to(character.position) <= (near_towers.attack_range + 20.0)]
                
                if (len(attackable_tower) > 0):
                    random_target = random.choice(attackable_tower)

                if (len(attackable_tower) > 0 and 
                    random_target.health < 500 and not random_target.is_fountain):
                    pass
                elif (len(near_tower) > 0):
                    random_target = random.choice(near_tower)
                elif (len(attackable_sniper) > 0):
                    random_target = random.choice(attackable_sniper)
                elif (len(attackable_ranger) > 0):
                    random_target = random.choice(attackable_ranger)
                else:
                    random_target = random.choice(attackable)

                self.api.action_cast_ability([character], position = random_target.position)                    
                self.api.action_attack([character], random_target)

            else:
                self.api.action_wander([character])
                for tower in self.visible_enemy_towers:
                    
                    attack_threshold = tower.attack_range + 7.0
                    target_position = pg.Vector2(0, 0)

                    for character in self.owned_characters:
                        if any(character.position.distance_to(tower.position) <= attack_threshold for tower in self.visible_enemy_towers):
                            self.api.action_move_to([character], target_position)
                            continue
                            
                    
        
    def handle_attack(self):
        
        if (len(self.api.get_owned_towers()) <= 1):
            self.api.action_wander(self.owned_characters)
            
            if (len(self.visible_enemy) + len(self.visible_enemy_towers) > 0):
                self.effective_attack()

        else:
            if (len(self.owned_characters) < 15 and len(self.owned_towers) <= 1):
                if (len(self.owned_characters) > len(self.visible_enemy) and len(self.visible_enemy) > 0):
                    self.effective_attack()
                else:
                    self.api.action_move_to(self.owned_characters[:], pg.Vector2(20, 20))
                
            elif (len(self.visible_enemy) > 0 and len(self.owned_characters) - len(self.visible_enemy) > 15):
                self.effective_attack()
            else:                
                if (len(self.visible_enemy_towers) > 0):
                    self.effective_attack()
                else:
                    self.api.action_wander(self.owned_characters)
                
                
        
        # raise NotImplementedError
        
    def run(self, api: API):
        self.api = api
        self.initialize()
        self.send_spam_message()
        
        # self.print_scores()
        
        
        self.handle_spawn()
        self.handle_attack()
        
        
strategy = Strategy()

def every_tick(api: API):
    
    strategy.run(api)