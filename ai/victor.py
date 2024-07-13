import math, itertools
import random

import pygame as pg

from api.prototype import *

entity_type = ['melee']
map = set((x, y) for x in range(18) for y in range(18))
        
my_team_id = 0
alive: dict[int, Character | Tower] = dict()
idle_melee, idle_ranger, idle_sniper, my_tower, my_character = [], [], [], [], []
enemys, enemys_tower, enemys_melee, enemys_ranger, enemys_sniper = [], [], [], [], []
walker: list[Character] = []
last_time_attack = {}
enemys_died = set()
hash_val = 48763
stop = {}
def handle_walker(api: API):
    global map, idle_melee, my_character, walker
    walker = [character for character in my_character if character.type is CharacterClass.MELEE]
    for w in walker:
        if api.get_movement(w).status is MovementStatusClass.STOPPED:
            choose = random.choice(list(map))
            for _ in range(25):
                x, y = min((random.random() + choose[0]) * 14, 245), min((random.random() + choose[1]) * 14, 245)
                if (api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OBSTACLE
                    and api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OUT_OF_BOUNDS):
                    api.action_move_to([w], pg.Vector2(x, y))
                    break


def init(api: API):
    global my_team_id, map, alive, walker, enemys_tower, my_tower, my_character
    my_team_id = api.get_team_id()
    my_character = api.get_owned_characters()
    enemys_tower = [tower for tower in api.get_visible_towers() if tower.team_id != my_team_id]
    my_tower = api.get_owned_towers()
    alive.clear()
    for character in itertools.chain(api.get_visible_characters(), api.get_visible_towers()):
        alive[character.id] = character

    for melee in my_character:
        if melee.type is CharacterClass.MELEE and (melee.position[0] // 14, melee.position[1] // 14) in map:
            map.remove((melee.position[0] // 14, melee.position[1] // 14))
    api.action_cast_ability([character for character in my_character if character.type == CharacterClass.MELEE or character.type == CharacterClass.SNIPER])

def every_tick(api: API):
    global my_team_id, map, alive, walker
    global my_character, my_tower, idle_melee, idle_ranger, idle_sniper, enemys, enemys_tower, enemys_melee, enemys_ranger, enemys_sniper
    init(api)
    if len(map) > 200:
        for tower in my_tower:
            api.change_spawn_type(tower, CharacterClass.MELEE)
    else:
        if len(walker) < 2:
            for tower in my_tower:
                api.change_spawn_type(tower, CharacterClass.MELEE)
        else:
            for tower in my_tower:
                api.change_spawn_type(tower, CharacterClass.SNIPER)
    handle_walker(api)
    for x in api.get_owned_characters():
        if x.type is CharacterClass.SNIPER:
            if x.id not in stop:
                for y in [tower for tower in api.get_visible_towers() if tower.team_id != my_team_id]:
                    if y.position.distance_to(x.position) < 55:
                        api.action_move_clear([x])
                        stop[x.id] = 1
                        break
                    else:
                        api.action_move_to([x], pg.Vector2(x.id % 250, 250 - x.id % 250))
            victim = None
            now_time = api.get_current_time()
            if x.id not in last_time_attack or now_time - last_time_attack[x.id] >= 2:
                for y in [character for character in api.get_visible_characters() if character.team_id != my_team_id]:
                    if y.position.distance_to(x.position) < x.attack_range and y.id not in enemys_died:
                        victim = y
                        break
                if victim is None:
                    continue
                api.action_attack([x], victim)
                last_time_attack[x.id] = now_time
                if victim.type is CharacterClass.RANGER or victim.type is CharacterClass.SNIPER or victim.health < 150:
                    enemys_died.add(y.id)
                else:
                    victim.health -= 150
