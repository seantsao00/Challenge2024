import math
import random

import pygame as pg

from api.prototype import *

def every_tick(api: API):

    visible = [character for character in api.get_visible_characters() if character.team_id !=
               api.get_team_id()]
    api.action_move_to(api.get_owned_characters(), pg.Vector2(random.random() * 250, random.random() * 250))
    if len(visible):
        api.action_move_to(api.get_owned_characters()[1:], visible[0].position)
        api.action_attack(api.get_owned_characters()[1:], visible[0])
