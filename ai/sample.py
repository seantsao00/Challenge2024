import math
import random

import pygame as pg

from api.prototype import *


def every_tick(api: API):
    visible = [character for character in api.get_visible_characters() if character.team_id !=
               api.get_team_id()]
    api.action_move_along(api.get_owned_characters()[:1],
                          pg.Vector2(2 * math.cos(api.get_current_time() / 20),
                                     2 * math.sin(api.get_current_time() / 20)))
    if len(visible):
        api.action_move_to(api.get_owned_characters()[1:], visible[0].position)
        api.action_attack(api.get_owned_characters()[1:], visible[0])
