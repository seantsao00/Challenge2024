import math
import random

import pygame as pg

from api.prototype import *

all_ch_id = set()

def every_tick(api: API):
    api.send_chat(f"我要開著我的 AE86 衝過去了")
    for character in api.get_owned_characters():
        all_ch_id.add(character.id)
    def attack_nearest_or_wander(characters: list[Character]):
        for character in characters:
            attackable_characters = api.within_attacking_range(character, api.get_visible_characters())
            attackable_enemy_characters = []
            for attackable_character in attackable_characters:
                if attackable_character.team_id != api.get_team_id():
                    attackable_enemy_characters.append(attackable_character)

            api.sort_by_distance(attackable_enemy_characters, character.position)
            if len(attackable_enemy_characters):
                api.action_attack([character], attackable_enemy_characters[0])
            else:
                api.action_wander([character])
    def simple_attack(characters: list[Character]):
        for character in characters:
            attackable_characters = api.within_attacking_range(character, api.get_visible_characters())
            attackable_enemy_characters = []
            for attackable_character in attackable_characters:
                if attackable_character.team_id != api.get_team_id():
                    attackable_enemy_characters.append(attackable_character)

            api.sort_by_distance(attackable_enemy_characters, character.position)
            if len(attackable_enemy_characters):
                api.action_cast_ability([character for character in characters if character.type != CharacterClass.RANGER])
                api.action_cast_ability([character for character in characters if character.type == CharacterClass.RANGER], position=attackable_enemy_characters[0].position)

                api.action_attack([character], attackable_enemy_characters[0])
    
    rand = random.randint(1, 3)
    for tower in api.get_owned_towers():
        if api.get_current_time() <= 8:
            api.change_spawn_type(tower, CharacterClass.MELEE)
        else:
            total = len(all_ch_id) % 8
            if total in [0, 1, 2]:
                api.change_spawn_type(tower, CharacterClass.MELEE)
            elif total in [4, 5]:
                api.change_spawn_type(tower, CharacterClass.RANGER)
            else:
                api.change_spawn_type(tower, CharacterClass.SNIPER)
        
        
    doing = set()
    for tower in api.get_visible_towers():
        if tower.is_fountain:
            continue
        
        moved_characters = []
        for character in api.get_owned_characters():
            rang = 80 if tower.team_id == 0 else 50
            if character.position.distance_to(tower.position) <= rang and character.id not in doing:
                moved_characters.append(character)
                doing.add(character.id)
        
        if tower.team_id == api.get_team_id():
            for character in moved_characters:
                if character.position.distance_to(tower.position) >= 10:
                    api.action_move_to(moved_characters, tower.position)
                simple_attack([character])
        elif tower.team_id == 0 or api.get_current_time() <= 75:
            api.action_attack([character for character in api.get_owned_characters() if character.id % 2 == 1], tower)
            api.action_cast_ability([character for character in api.get_owned_characters() if character.id % 2 == 1 and character.type != CharacterClass.RANGER])
            api.action_cast_ability([character for character in api.get_owned_characters() if character.id % 2 == 1 and character.type == CharacterClass.RANGER], position = tower.position)

            simple_attack([character for character in api.get_owned_characters() if character.id % 2 != 1])
            api.action_move_to(moved_characters, tower.position)
            
        else:
            api.action_move_to(moved_characters, tower.position)
            simple_attack(moved_characters)
    
    for character in api.get_owned_characters():
        all_not_work = []
        if not character.id in doing:
            all_not_work.append(character)
        attack_nearest_or_wander(all_not_work)

        

