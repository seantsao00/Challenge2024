import math, itertools
import random

import pygame as pg

from api.prototype import *

entity_type = ['melee']
map = set((x, y) for x in range(18) for y in range(18))
        
gathering_point = pg.Vector2(20, 20)
at_gathering_point = dict()
attacker_melee: list[list[int]] = []
attacker_ranger: list[list[int]] = []
destination: list[int] = []
my_team_id = 0
alive: dict[int, Character | Tower] = dict()
used = set()

def count_defence(total_health, damage):
    if total_health > damage / 2 * 3:
        return 3 + (total_health - damage / 2 * 3) / damage
    return total_health / (damage / 2)

def handle_attack(api: API):
    global gathering_point, my_team_id, attacker_melee, attacker_ranger, destination, alive
    need_delete = set()
    for i in range(len(destination)):
        print(len(attacker_melee[i]), len(attacker_ranger[i]))
        attacker_melee[i] = [melee for melee in attacker_melee[i] if melee in alive]
        attacker_ranger[i] = [ranger for ranger in attacker_ranger[i] if ranger in alive]
        if (len(attacker_ranger[i]) == 0 or len(attacker_melee[i]) == 0 or alive[destination[i]].team_id == my_team_id
            or (isinstance(destination[i], Character) and destination[i] not in alive)):
            print("delete", i, len(attacker_ranger[i]), len(attacker_melee[i]))
            need_delete.add(i)
            continue

        if alive[attacker_melee[i][0]].position.distance_to(alive[attacker_ranger[i][0]].position) > 18:
            api.action_move_clear([alive[x] for x in attacker_melee[i]])
        else:
            api.action_move_to([alive[x] for x in attacker_ranger[i]], alive[destination[i]].position)
            api.action_move_to([alive[x] for x in attacker_melee[i]], alive[destination[i]].position)

        if alive[attacker_melee[i][0]].position.distance_to(alive[destination[i]].position) < alive[attacker_melee[i][0]].attack_range - 0.1:
            api.action_move_clear([alive[x] for x in attacker_melee[i]])
            api.action_attack([alive[x] for x in attacker_melee[i]], alive[destination[i]])
            print("attack", attacker_melee[i], alive[destination[i]])

        if alive[attacker_ranger[i][0]].position.distance_to(alive[destination[i]].position) < alive[attacker_ranger[i][0]].attack_range - 0.1:
            api.action_move_clear([alive[x] for x in attacker_ranger[i]])
            api.action_attack([alive[x] for x in attacker_ranger[i]], alive[destination[i]])
            print("attack", attacker_ranger[i], alive[destination[i]])
    
    attacker_melee = [attacker_melee[i] for i in range(len(attacker_melee)) if i not in need_delete]
    attacker_ranger = [attacker_ranger[i] for i in range(len(attacker_ranger)) if i not in need_delete]
    destination = [destination[i] for i in range(len(destination)) if i not in need_delete]


def every_tick(api: API):
    global my_team_id, map, alive, gathering_point, attacker_melee, attacker_ranger, destination
    my_team_id = api.get_team_id()
    visible = api.get_visible_characters()
    my_character = api.get_owned_characters()
    my_melee = [melee for melee in my_character if melee.type == CharacterClass.MELEE and melee.id not in used]
    my_ranger = [ranger for ranger in my_character if ranger.type == CharacterClass.RANGER and ranger.id not in used]
    my_sniper = [sniper for sniper in my_character if sniper.type == CharacterClass.SNIPER and sniper.id not in used]
    my_tower = api.get_owned_towers()
    visible_tower = [tower for tower in api.get_visible_towers() if tower.team_id != my_team_id]
    visible_enemy= [character for character in visible if character.team_id != my_team_id]
    
    alive.clear()
    for character in itertools.chain(visible, my_character, my_tower, visible_tower):
        alive[character.id] = character

    handle_attack(api)

    api.action_move_to(my_ranger, gathering_point)
    api.action_cast_ability(my_melee)

    if len(my_melee) < 8:
        for tower in my_tower:
            api.change_spawn_type(tower, CharacterClass.MELEE)

    if len(map) > 0:
        for melee in my_melee:
            if (melee.position[0] // 14, melee.position[1] // 14) in map:
                map.remove((melee.position[0] // 14, melee.position[1] // 14))
        mx = len(my_melee)
        if len(visible_tower) > 0:
            mx = min(8, mx)
        for i in range(mx):
            w = my_melee[i]
            print("in", i, w.position, api.get_movement(w).status)
            if api.get_movement(w).status is not MovementStatusClass.TO_POSITION:
                choose = random.choice(list(map))
                for _ in range(25):
                    x, y = min((random.random() + choose[0]) * 14, 245), min((random.random() + choose[1]) * 14, 245)
                    if (api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OBSTACLE
                        and api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OUT_OF_BOUNDS):
                        api.action_move_to([w], pg.Vector2(x, y))
                        break
        api.action_move_to(my_melee[mx + 1:], gathering_point)
        
    

    if len(visible_tower) > 0:
        best_choose = (1e9, None)
        for tower in visible_tower:
            total = 150
            for character in visible_enemy:
                if character.type is CharacterClass.MELEE:
                    total += 36
                elif character.type is CharacterClass.RANGER:
                    total += 72
                elif character.type is CharacterClass.SNIPER:
                    total += 150
            best_choose = min(best_choose, (total, tower))
        if len(my_ranger) < 8:
            for tower in my_tower:
                api.change_spawn_type(tower, CharacterClass.RANGER)
        else:
            for tower in my_tower:
                api.change_spawn_type(tower, CharacterClass.RANGER)
        my_total_health = 0
        for melee in my_melee:
            if melee.position.distance_to(gathering_point) < 0.1:
                my_total_health += melee.health
        group_melee = [_.id for _ in my_melee if _.position.distance_to(gathering_point) < 0.1]
        group_ranger = [_.id for _ in my_ranger if _.position.distance_to(gathering_point) < 0.1]
        if len(group_ranger) >= 8 and count_defence(my_total_health, best_choose[0]) > 5:
            # print("append attack", len(destination))
            attacker_melee.append(group_melee)
            attacker_ranger.append(group_ranger)
            destination.append(best_choose[1].id)
            for character in itertools.chain(group_melee, group_ranger):
                if alive[character].position.distance_to(gathering_point) < 0.1:
                    used.add(character)
            
