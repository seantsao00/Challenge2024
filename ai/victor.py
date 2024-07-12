import math, itertools
import random

import pygame as pg

from api.prototype import *

entity_type = ['melee']
map = set((x, y) for x in range(18) for y in range(18))
        
gathering_point = pg.Vector2(20, 20)
attacker_team: list[list[list[int], list[int], list[int], int]] = []
sniper_under_tower: dict[int, int] = {}
my_team_id = 0
alive: dict[int, Character | Tower] = dict()
idle_melee, idle_ranger, idle_sniper, my_tower, my_character = [], [], [], [], []
enemys, enemys_tower, enemys_melee, enemys_ranger, enemys_sniper = [], [], [], [], []
defense: dict[int, list[list[Character], list[Character], list[Character]]] = dict()
walker: list[Character] = []

def count_attack_tower(damage: float, tower: Tower):
    global idle_melee, idle_ranger, idle_sniper
    total_health = 0
    for x in idle_melee:
        total_health += x.health
    if len(idle_ranger) >= 5 and total_health > 6 * damage: # 6s get tower
        group_ranger, group_melee = [], []
        group_ranger = [idle_ranger[i].id for i in range(5)]
        total_health = 6 * damage
        for x in idle_melee:
            total_health -= x.health
            group_melee.append(x.id)
            if total_health < 0:
                break
        attacker_team.append([group_melee, group_ranger, [], tower.id])
        del idle_ranger[:5]
        del idle_melee[:len(group_melee)]

def attack_enemy(api: API, enemy):
    global alive, attacker_team, idle_melee, idle_ranger, idle_sniper
    # print('attack', len(idle_ranger), len(idle_melee))
    if len(idle_ranger) >= 3 and enemy.type is not CharacterClass.SNIPER:
        attacker_team.append([[], [idle_ranger[x].id for x in range(3)], [], enemy.id])
        print("add attack", idle_ranger[:3])
        del idle_ranger[:3]
    elif len(idle_melee) >= 3 and (enemy.type is CharacterClass.MELEE or enemy.type is CharacterClass.SNIPER):
        attacker_team.append([[idle_melee[x].id for x in range(3)], [], [], enemy.id])
        del idle_melee[:3]

def handle_attack(api: API):
    global gathering_point, my_team_id, attacker_melee, attacker_ranger, destination, alive
    need_delete = set()
    for i in range(len(attacker_team)):
        total_size = 0
        attribute: list[tuple[pg.Vector2, float]] = [(None, 0), (None, 0), (None, 0)]
        for j in range(3):
            attacker_team[i][j] = [character for character in attacker_team[i][j] if character in alive]
        for j in range(3):
            if len(attacker_team[i][j]) != 0:
                total_size += len(attacker_team[i][j])
                attribute[j] = (alive[attacker_team[i][j][0]].position, alive[attacker_team[i][j][0]].attack_range)

        if (total_size == 0 or attacker_team[i][3] not in alive or alive[attacker_team[i][3]].team_id == my_team_id):
            print('delete', attacker_team[i][0], attacker_team[i][1], attacker_team[i][2])
            need_delete.add(i)
            continue
        
        for j in range(3):
            if attribute[j][0] is not None and attribute[j][0].distance_to(alive[attacker_team[i][3]].position) < attribute[j][1]:
                api.action_move_clear([alive[_] for _ in attacker_team[i][j]])
                api.action_attack([alive[_] for _ in attacker_team[i][j]], alive[attacker_team[i][3]])
                if j == 1:
                    api.action_cast_ability([alive[_] for _ in attacker_team[i][j]], position=alive[attacker_team[i][3]].position)
            else:
                api.action_move_to([alive[_] for _ in attacker_team[i][j]], alive[attacker_team[i][3]].position)

        for j in range(3):
            for k in range(j + 1, 3):
                if attribute[j][0] is not None and attribute[k][0] is not None:
                    if attribute[j][0].distance_to(attribute[k][0]) >  attribute[k][1] - attribute[j][1] + 3:
                        print("clear")
                        api.action_move_clear([alive[_] for _ in attacker_team[i][j]])
                        break

    for x in need_delete:
        for j in range(3):
            api.action_move_to([alive[_] for _ in attacker_team[x][j]], gathering_point)
    attacker_team = [attacker_team[_] for _ in range(len(attacker_team)) if _ not in need_delete]

def handle_walker(api: API):
    global map, idle_melee
    if len(map) == 0:
        api.action_move_to([alive[i] for i in walker], gathering_point)
        walker.clear()
        return
    
    for i in walker:
        w = alive[i]
        if api.get_movement(w).status is MovementStatusClass.STOPPED:
            choose = random.choice(list(map))
            for _ in range(25):
                x, y = min((random.random() + choose[0]) * 14, 245), min((random.random() + choose[1]) * 14, 245)
                if (api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OBSTACLE
                    and api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OUT_OF_BOUNDS):
                    api.action_move_to([w], pg.Vector2(x, y))
                    break

def tower_generate(api: API):
    global idle_melee, idle_ranger, idle_sniper, enemys, enemys_tower, enemys_melee, enemys_ranger, enemys_sniper, my_tower
    for tower in my_tower:
        if len(idle_melee) <= len(idle_ranger) or (len(enemys_tower) == 0 and len(enemys) == 0):
            api.change_spawn_type(tower, CharacterClass.MELEE)
        else:
            api.change_spawn_type(tower, CharacterClass.RANGER)

def init(api: API):
    global my_team_id, map, alive, gathering_point, attacker_team, walker
    global my_character, idle_melee, idle_ranger, idle_sniper, enemys, enemys_tower, enemys_melee, enemys_ranger, enemys_sniper, my_tower
    new_character = list(set(i.id for i in api.get_owned_characters()) - (set(i.id for i in my_character) & set(i.id for i in api.get_owned_characters())))
    # print("new", new_character)
    my_team_id = api.get_team_id()
    visible = api.get_visible_characters()
    my_character = api.get_owned_characters()
    idle_melee = [melee for melee in my_character if melee.type == CharacterClass.MELEE and melee.position.distance_to(gathering_point) < 1]
    idle_ranger = [ranger for ranger in my_character if ranger.type == CharacterClass.RANGER and ranger.position.distance_to(gathering_point) < 1]
    idle_sniper = [sniper for sniper in my_character if sniper.type == CharacterClass.SNIPER and sniper.position.distance_to(gathering_point) < 1]
    visible_enemy = [character for character in visible if character.team_id != my_team_id]
    my_tower = api.get_owned_towers()
    enemys = api.sort_by_distance(visible_enemy, gathering_point)
    enemys_tower = [tower for tower in api.get_visible_towers() if tower.team_id != my_team_id and tower.is_fountain is False]
    enemys_melee = [x for x in enemys if x.type is CharacterClass.MELEE]
    enemys_ranger = [x for x in enemys if x.type is CharacterClass.RANGER]
    enemys_sniper = [x for x in enemys if x.type is CharacterClass.SNIPER]
    alive.clear()
    for character in itertools.chain(visible, api.get_visible_towers()):
        alive[character.id] = character
    walker = [w for w in walker if w in alive]
    api.action_move_to([alive[i] for i in new_character], gathering_point)
    for melee in my_character:
        if melee.type is CharacterClass.MELEE and (melee.position[0] // 14, melee.position[1] // 14) in map:
            map.remove((melee.position[0] // 14, melee.position[1] // 14))

def every_tick(api: API):
    global my_team_id, map, alive, walker, gathering_point, attacker_team
    global my_character, my_tower, idle_melee, idle_ranger, idle_sniper, enemys, enemys_tower, enemys_melee, enemys_ranger, enemys_sniper
    init(api)
    if len(map) > 0:
        if len(enemys_tower) == 0 and len(enemys) == 0:
            walker = walker + [melee.id for melee in idle_melee]
            idle_melee.clear()
        elif len(enemys_tower) == 0:
            api.action_move_to([alive[walker[i]] for i in range(4, len(walker))], gathering_point)
            walker = walker[:4]
            while len(walker) < 4 and len(idle_melee) > 0:
                walker.append(idle_melee[-1].id)
                idle_melee.pop()
            print('set to 4', len(walker))
        else:
            print('clear')
            api.action_move_to([alive[i] for i in walker], gathering_point)
            walker.clear()

    handle_attack(api)
    handle_walker(api)
    tower_generate(api)
    api.action_cast_ability([character for character in my_character if character.type is CharacterClass.MELEE])
    api.action_cast_ability([character for character in my_character if character.type is CharacterClass.SNIPER])


    best_choose = (1e9, None)
    for tower in enemys_tower:
        total = 150
        for character in enemys:
            if character.type is CharacterClass.MELEE:
                total += 18
            elif character.type is CharacterClass.RANGER:
                total += 36
            elif character.type is CharacterClass.SNIPER:
                total += 75
        best_choose = min(best_choose, (total, tower))

    for enemy in enemys:
        if gathering_point.distance_to(enemy.position) < 75:
            attack_enemy(api, enemy)
            
    if best_choose[0] < 600:
        count_attack_tower(best_choose[0], best_choose[1])
    else:   
        for enemy in enemys:
            if gathering_point.distance_to(enemy.position) >= 75:
                attack_enemy(api, enemy)
    
    