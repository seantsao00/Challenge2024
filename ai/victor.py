import math, itertools
import random

import pygame as pg

from api.prototype import *

map = set((x, y) for x in range(16) for y in range(16))
        
my_team_id = 0
alive: dict[int, Character | Tower] = dict()
idle_melee, idle_ranger, idle_sniper, my_tower, my_character = [], [], [], [], []
enemys, enemys_tower, enemys_melee, enemys_ranger, enemys_sniper = [], [], [], [], []
walker: list[Character] = []
need_change_position: set[tuple[int, int]] = []
last_time_attack = {}
enemys_died = set()
destination = []
stop = {}
stop_at: dict[tuple[int, int], int] = {}

def handle_walker(api: API):
    global map, idle_melee, my_character, walker
    walker = [character for character in my_character if character.type is CharacterClass.MELEE]
    for w in walker:
        if api.get_movement(w).status is MovementStatusClass.STOPPED:
            choose = random.choice(list(map))
            for _ in range(25):
                x, y = min((random.random() + choose[0]) * 16, 245), min((random.random() + choose[1]) * 16, 245)
                if (api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OBSTACLE
                    and api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OUT_OF_BOUNDS):
                    api.action_move_to([w], pg.Vector2(x, y))
                    break


def init(api: API):
    global my_team_id, map, alive, walker, enemys_tower, my_tower, my_character, need_change_position
    if len(destination) == 0:
        for x in range(1, 250):
            t = 1
            while t > 0:
                if api.get_terrain(pg.Vector2(x, 250 - x) * t) is not MapTerrain.OBSTACLE:
                    destination.append(pg.Vector2(x, 250 - x) * t)
                    break
                t -= 0.01
    my_team_id = api.get_team_id()
    my_character = api.get_owned_characters()
    enemys_tower = [tower for tower in api.get_visible_towers() if tower.team_id != my_team_id]
    my_tower = api.get_owned_towers()
    alive.clear()
    for character in itertools.chain(api.get_visible_characters(), api.get_visible_towers()):
        alive[character.id] = character

    need_change_position = set(_ for _ in need_change_position if _[0] in alive)
    for melee in my_character:
        if melee.type is CharacterClass.MELEE and (melee.position[0] // 16, melee.position[1] // 16) in map:
            map.remove((melee.position[0] // 16, melee.position[1] // 16))
    api.action_cast_ability([character for character in my_character if character.type == CharacterClass.MELEE or character.type == CharacterClass.SNIPER])

def change_position(api: API):
    global need_change_position, need_add, stop_at, stop, destination
    need_delete = []
    need_add = []
    for x in need_change_position:
        en = alive[x[0]]
        tw = alive[x[1]]
        if (en.position.x // 25, en.position.y // 25) not in stop_at:
            stop_at[(en.position.x // 25, en.position.y // 25)] = 1
            need_delete.append(x)
        elif stop_at[(en.position.x // 25, en.position.y // 25)] < 5:
            stop_at[(en.position.x // 25, en.position.y // 25)] += 1
            need_delete.append(x)
        else:
            danger = [tower.id for tower in api.get_visible_towers() if tower.team_id != my_team_id and tower.position.distance_to(en.position) <= 50]
            if len(danger) > 1:
                if x[1] == danger[0]:
                    api.action_move_along([en], (en.position - alive[danger[0]].position) * -1)
                else:
                    api.action_move_along([en], (en.position - alive[danger[1]].position) * -1)
            elif len(danger) == 1:
                need_delete.append(x)
                need_add.append((x[0], danger[0]))
                api.action_move_along([en], pg.Vector2(-(en.position.y - alive[danger[0]].position.y), (en.position.x - alive[danger[0]].position.y)))
            else:
                api.action_move_to([en],  destination[en.id % len(destination)])
                del stop[en.id]
                need_delete.append(x)

    for x in need_delete:
        need_change_position.remove(x)

def every_tick(api: API):
    global my_team_id, map, alive, walker, stop_at, need_change_position
    global my_character, my_tower, idle_melee, idle_ranger, idle_sniper, enemys, enemys_tower, enemys_melee, enemys_ranger, enemys_sniper
    init(api)
    if len(map) > 140:
        for tower in my_tower:
            api.change_spawn_type(tower, CharacterClass.MELEE)
    else:
        if len(walker) < 2 and len(map) > 0: 
            for tower in my_tower:
                api.change_spawn_type(tower, CharacterClass.MELEE)
        else:
            for tower in my_tower:
                api.change_spawn_type(tower, CharacterClass.SNIPER)
    handle_walker(api)
    change_position(api)
    for x in api.get_owned_characters():
        if x.type is CharacterClass.SNIPER:
            now_time = api.get_current_time()    
            if x.id not in last_time_attack or now_time - last_time_attack[x.id] >= 2:
                if x.id not in stop:
                    api.action_move_to([x], destination[x.id % len(destination)])
                    for y in [tower for tower in api.get_visible_towers() if tower.team_id != my_team_id]:
                        if y.position.distance_to(x.position) < 50:
                            api.action_move_clear([x])
                            if (x.position.x // 25, x.position.y // 25) not in stop_at:
                                stop_at[(x.position.x // 25, x.position.y // 25)] = 1
                            elif stop_at[(x.position.x // 25, x.position.y // 25)] < 4:
                                stop_at[(x.position.x // 25, x.position.y // 25)] += 1
                            else:
                                need_change_position.add((x.id, y.id))
                            stop[x.id] = 1
                            break
                victim = None
                now_time = api.get_current_time()
                for y in [character for character in api.get_visible_characters() if character.team_id != my_team_id]:
                    if y.position.distance_to(x.position) < x.attack_range and y.id not in enemys_died:
                        victim = y
                        break
                if victim is None:
                    continue
                api.action_move_clear([x])
                api.action_attack([x], victim)
                last_time_attack[x.id] = now_time
                if victim.type is CharacterClass.RANGER or victim.type is CharacterClass.SNIPER or victim.health < 150:
                    enemys_died.add(y.id)
                else:
                    victim.health -= 150
