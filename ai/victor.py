import math
import random

import pygame as pg

from api.prototype import *

entity_type = ['melee']
map = [(x, y) for x in range(18) for y in range(18)]
        
gathering_point = pg.Vector2(10, 10)
at_gathering_point = dict()

def every_tick(api: API):
    my_team_id = api.get_team_id()
    visible = api.get_visible_characters()
    my_character = api.get_owned_characters()
    my_melee = [melee for melee in my_character if melee.type == CharacterClass.MELEE]
    my_ranger = [ranger for ranger in my_character if ranger.type == CharacterClass.MELEE]
    my_sniper = [sniper for sniper in my_character if sniper.type == CharacterClass.MELEE]
    my_tower = api.get_owned_towers()
    visible_tower = [tower for tower in api.get_visible_towers() if tower.team_id != my_team_id]
    visible_enemy= [character for character in visible if character.team_id != my_team_id]

    for tower in my_tower:
        api.change_spawn_type(tower, CharacterClass.MELEE)

    api.action_cast_ability(my_melee)
    global map

    if len(map) > 0:
        mx = len(my_melee)
        if len(visible_tower) > 0:
            mx = 4
        for i in range(mx):
            w = my_melee[i]
            # print("in", i, w.position, api.get_movement(w).status)
            if api.get_movement(w).status is MovementStatusClass.STOPPED:
                if (w.position[0] // 14, w.position[1] // 14) in map:
                    map.remove((w.position[0] // 14, w.position[1] // 14))
                choose = random.choice(map)
                for _ in range(25):
                    x, y = min((random.random() + choose[0]) * 14, 245), min((random.random() + choose[1]) * 14, 245)
                    if (api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OBSTACLE
                        and api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OUT_OF_BOUNDS):
                        api.action_move_to([w], pg.Vector2(x, y))
                        break
 

    # if len(visible_tower) > 0:
    #     best_choose = (1e9, None)
    #     for tower in visible_tower:
    #         total = 150
    #         for character in visible_enemy:
    #             if character.type is CharacterClass.MELEE:
    #                 total += 36
    #             elif character.type is CharacterClass.RANGER:
    #                 total += 72
    #             elif character.type is CharacterClass.SNIPER:
    #                 total += 150
    #         best_choose = min(best_choose, (total, tower))





    

    
