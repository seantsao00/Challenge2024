from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventAttack
from instances_manager import get_event_manager, get_model
from model.character import Character

if TYPE_CHECKING:
    from model.team import Team


class Ranger(Character):
    """
    Class for the ranger fighter
    Ranger fighter has the following unique moves:
     - area_attack: Attack a locations and damage all nearby foes.
    """

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team):
        super().__init__(position, team, const.RANGER_ATTRIBUTE, const.CharacterType.RANGER, None)

    def abilities(self, *args, **kwargs):
        if len(args) < 1 or not isinstance(args[0], pg.Vector2):
            raise ValueError()
        target: pg.Vector2 = args[0]
        dist = self.position.distance_to(target)
        if dist <= self.attribute.attack_range:
            print("ranged ability attack")
            all_victim = get_model().grid.all_entity_in_range(target, self.attribute.ability_variables)
            for victim in all_victim:
                if self.team != victim.team:
                    get_event_manager().post(EventAttack(attacker=self, victim=victim), victim.id)
