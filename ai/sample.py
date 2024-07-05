import math

import pygame as pg
import random
import api.prototype as api


def every_tick(api: api.API):
    api.action_move_along(api.get_characters(),
                          pg.Vector2(1 * math.cos(api.get_time()),
                                     1 * math.sin(api.get_time())))
