import math
import random

import pygame as pg

from api.prototype import *


def every_tick(interface: API):
    visible = [character for character in interface.get_visible_characters()
               if character.team_id != interface.get_team_id()]
    interface.action_move_along(interface.get_owned_characters()[:1],
                                pg.Vector2(2 * math.cos(interface.get_current_time() / 20),
                                           2 * math.sin(interface.get_current_time() / 20)))
    if len(visible):
        interface.action_move_to(interface.get_owned_characters()[1:], visible[0].position)
        interface.action_attack(interface.get_owned_characters()[1:], visible[0])
