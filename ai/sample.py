import math

import pygame as pg

import api.prototype as api


def every_tick(api: api.API):
    print("begin compute")
    visible = api.look_characters()
    api.action_move_along(api.get_characters()[:1],
                          pg.Vector2(1.3 * math.cos(api.get_time()),
                                     1.3 * math.sin(api.get_time())))
    if len(visible):
        api.action_move_to(api.get_characters()[1:], visible[0].position)
        api.action_attack(api.get_characters()[1:], visible[0])
    print("end compute")
