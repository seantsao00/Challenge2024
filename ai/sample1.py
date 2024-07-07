import math

import pygame as pg
import random
import api.prototype as api

destination = []

def every_tick(api: api.API):
    character = api.get_characters()
    print(len(character))
    # if len(character) < 200:
    #     return
    while len(character) > len(destination):
        destination.append(pg.Vector2(random.random() * 250, random.random() * 250))
    for i, ch in enumerate(character):
        while ch._Character__position.distance_to(destination[i]) < 0.1:
            destination[i] = pg.Vector2(random.random() * 250, random.random() * 250)
        api.action_move_along([ch], pg.Vector2(destination[i].x - ch._Character__position.x, destination[i].y - ch._Character__position.y))
