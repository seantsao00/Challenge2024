import math
import random

import pygame as pg

from api.prototype import *


def every_tick(interface: API):
    interface.send_chat("為什麼要演奏春日影!!!")
    owned_towers = interface.get_owned_towers()
    for tower in owned_towers:
        interface.change_spawn_type(tower, random.choice([CharacterClass.MELEE, CharacterClass.RANGER, CharacterClass.SNIPER]))
    owned_characters = interface.get_owned_characters()
    interface.action_cast_ability(owned_characters)
    for ch in owned_characters:
        if not interface.get_movement(ch).is_wandering:
            interface.action_wander([ch])
    visible = [character for character in interface.get_visible_characters()
               if character.team_id != interface.get_team_id()]
    for enemy in visible:
        if enemy.team_id != interface.get_team_id():
            interface.action_attack(owned_characters, enemy)

