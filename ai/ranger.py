import math
import random

import pygame as pg

import api.prototype


def every_tick(interface: api.prototype.API):
    fountain = interface.get_owned_towers()[0]
    interface.action_cast_ability(
        [character for character in interface.get_owned_characters()
         if character.type is api.prototype.CharacterClass.RANGER],
        position=fountain.position)
