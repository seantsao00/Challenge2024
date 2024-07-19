# 五小
import math
import random
 
 
import pygame as pg
 
 
from api.prototype import *

class AiInfo():

    def __init__(self) -> None:
        self.team_id: int
        self.current_time: float
        self.character_type = [0,0,0]
        self.my_tower = []
        self.my_character = []

def calculate_distance(a: pg.Vector2, b: pg.Vector2):
    return (a-b).length()

def get_nearest_friend_melee(interface: API, position: pg.Vector2):
    my_characters = interface.get_owned_characters()
    my_melee = []
    for character in my_characters:
        if character.type is CharacterClass.MELEE:
            my_melee.append(character)
    if len(my_melee) == 0:
        return None
    my_melee = interface.sort_by_distance(my_melee, position)
    return my_melee[0]


def update(interface: API):
    info.character_type = [0, 0, 0]
    info.current_time = interface.get_current_time()
    info.my_tower = interface.get_owned_towers()
    info.my_character = interface.get_owned_characters()
    for unit in info.my_character:
        if unit.type == CharacterClass.MELEE:
            info.character_type[0] += 1
        elif unit.type == CharacterClass.RANGER:
            info.character_type[1] += 1
        else:
            info.character_type[2] += 1
    print(f'Melee: {info.character_type[0]}, ranger: {info.character_type[1]}, sniper: {info.character_type[2]}')
 
def set_character_type(interface: API, c_type , tower: Tower, m, r, s):
    ratio = random.random() * 100
    if ratio < m:
        interface.change_spawn_type(tower,CharacterClass.MELEE)
    elif ratio < m + r:
        interface.change_spawn_type(tower,CharacterClass.RANGER)
    elif ratio < m+ r + s:
        interface.change_spawn_type(tower,CharacterClass.SNIPER)
 
info = AiInfo()
 
def every_tick(interface: API):
 
    update(interface)
    
    visible_tower = []
    visible_character = []

    for tower in interface.get_visible_towers():
        if tower.team_id != interface.get_team_id() and tower.is_fountain == False:
            visible_tower.append(tower)
    for character in interface.get_visible_characters():
        if character.team_id != interface.get_team_id():
            visible_character.append(character)

    if info.current_time < 20:
        set_character_type(interface, info.character_type, info.my_tower[0], 100, 0, 0)
    else:
        if len(visible_tower) and len(info.my_tower) >= 1:
            set_character_type(interface, info.character_type, info.my_tower[0], 50, 50, 0)
        elif len(info.my_tower) != 1:
            '''
            if info.character_type[2] < 5:
                set_character_type(interface, info.character_type, info.my_tower[1], 10, 30, 60)
            else:
                set_character_type(interface, info.character_type, info.my_tower[1], 50, 50, 0)
            '''
            set_character_type(interface, info.character_type, info.my_tower[1], 0, 0, 100)
        else:
            set_character_type(interface, info.character_type, info.my_tower[0], 60, 30, 10)
    sniper_list = []
    for unit in info.my_character:
        if unit.type is CharacterClass.SNIPER:
            interface.action_cast_ability(unit)
            if len(visible_character):
                target = interface.within_attacking_range(unit, visible_character)
                if len(target):
                    if unit.team_id != target[0].team_id:
                        interface.action_attack(unit, target[0])
            sniper_list.append(unit)
        
        if unit.type is CharacterClass.MELEE:
            interface.action_cast_ability(unit)
            if len(visible_tower):
                enemy = interface.within_attacking_range(unit, visible_tower)
                if len(enemy):
                    interface.action_attack(unit, enemy[0])
                    print(enemy[0],"攻擊")
                else:
                    interface.action_move_to(unit, visible_tower[0].position)

            elif len(visible_character):
                enemy = interface.within_attacking_range(unit, visible_character)
                if len(enemy):
                    for attack in enemy:
                        if attack.health % 10 == 0:
                            interface.action_attack(unit, attack)
                else:
                    interface.action_move_to(unit, visible_character[0].position)
            else:
                interface.action_wander(unit)
        
        if unit.type is CharacterClass.RANGER:
            nearest_friend_melee = get_nearest_friend_melee(interface, unit.position)
            if nearest_friend_melee is not None:
                interface.action_move_to(unit, get_nearest_friend_melee(interface, unit.position).position)
            else:
                interface.action_wander(unit)

            if len(visible_tower):
                enemy = interface.within_attacking_range(unit, visible_tower)
                if len(enemy):
                    interface.action_attack(unit, enemy[0])
                    interface.action_cast_ability(unit)
                    print(enemy[0],"攻擊")
                else:
                    interface.action_move_to(unit, visible_tower[0].position)

            elif len(visible_character):
                interface.action_cast_ability(unit)
                enemy = interface.within_attacking_range(unit, visible_character)
                if len(enemy):
                    interface.action_attack(unit, enemy[0])
                    interface.action_cast_ability(unit)
                else:
                    interface.action_move_to(unit, visible_character[0].position)
    if len(sniper_list) > 5:
        set_character_type(interface, info.character_type, info.my_tower[1], 30, 30, 40)
        for _ in range(5, len(sniper_list)):
            interface.action_wander(sniper_list[_])