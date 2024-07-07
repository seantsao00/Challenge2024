import math

import pygame as pg

import api.prototype as api


def every_tick(api: api.API):
    visible = api.look_towers()
    api.action_move_along(api.get_characters()[:1],
                          pg.Vector2(1 * math.cos(api.get_time()),
                                     1 * math.sin(api.get_time())))
    if len(visible):
        print("attacck!")
        api.action_move_to(api.get_characters()[1:], visible[0].__position)
        api.action_attack(api.get_characters()[1:], visible[0])
