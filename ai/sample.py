import math
import random

import pygame as pg

import api.prototype as api


def every_tick(api: api.API):
    visible = [character for character in api.look_characters() if character.team_id !=
               api.get_team_id()]
    api.action_move_along(api.get_characters()[:1],
                          pg.Vector2(2 * math.cos(api.get_time() / 5),
                                     2 * math.sin(api.get_time() / 5)))
    if len(visible):
        api.action_move_to(api.get_characters()[1:], visible[0].position)
        api.action_attack(api.get_characters()[1:], visible[0])
