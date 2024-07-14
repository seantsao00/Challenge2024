import math
import random

import pygame as pg
from itertools import chain

from api.prototype import *


def every_tick(api: API):
    my_characters = api.get_owned_characters()
    attackable_towers = [tow for tow in api.get_visible_towers() if tow.team_id != api.get_team_id() and not tow.is_fountain]
    my_towers = api.get_owned_towers()
    opp_characters = [ch for ch in api.get_visible_characters() if ch.team_id != api.get_team_id()]
    
    melees = [ch for ch in my_characters if ch.type == CharacterClass.MELEE]
    rangers = [ch for ch in my_characters if ch.type == CharacterClass.RANGER]
    snipers = [ch for ch in my_characters if ch.type == CharacterClass.SNIPER]

    for tow in my_towers:
        if len(melees) > 30:
            if len(rangers) > len(snipers):
                api.change_spawn_type(tow, CharacterClass.SNIPER)
            else:
                api.change_spawn_type(tow, CharacterClass.RANGER)
        else:
            api.change_spawn_type(tow, CharacterClass.MELEE)

    api.action_wander(melees[0::2])
    if len(attackable_towers) > 0:
        api.action_move_to(melees[1::2], attackable_towers[0].position)
        api.action_attack(melees[1::2], attackable_towers[0])
        api.action_cast_ability([mel for mel in melees[1::2] if mel.position.distance_to(attackable_towers[0].position) < attackable_towers[0].attack_range])

        rs = chain(rangers, snipers)
        in_range, out_range = ([ch for ch in rs if ch.position.distance_to(attackable_towers[0]) < ch.attack_range],
                               [ch for ch in rs if ch.position.distance_to(attackable_towers[0]) >= ch.attack_range])
        
        api.action_move_to(out_range, attackable_towers[0].position)
        api.action_move_clear(in_range)

        api.action_attack(rs, attackable_towers[0])
    elif len(opp_characters) > 0:
        for ch in chain(melees[len(melees) // 2:], rangers, snipers):
            target = api.sort_by_distance(opp_characters, ch.position)[0]
            if ch.position.distance_to(target.position) < ch.attack_range / 2:
                api.action_move_along([ch], ch.position - target.position)
            else:
                api.action_move_to([ch], target.position)
            
            api.action_attack([ch], target)
    else:
        api.action_wander(chain(melees, rangers, snipers))
