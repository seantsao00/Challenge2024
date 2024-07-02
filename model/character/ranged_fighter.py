import pygame as pg

import const
from event_manager import EventMultiAttack
from instances_manager import get_event_manager
from model.character import Character


class RangedFighter(Character):
    """
    Class for the ranged fighter
    Ranged fighter has the following unique moves:
     - area_attack: Attack a locations and damage all nearby foes.
    """

    def __init__(self, team, position: pg.Vector2):
        super().__init__(position, team, const.RANGED_SPEED, const.RANGED_ATTACK_RANGE,
                         const.RANGED_DAMAGE, const.RANGED_HEALTH, const.RANGED_VISION)

    def abilities(self, origin: pg.Vector2, radius: float):
        dist = self.position.distance_to(origin)
        if dist <= self.attack_range:
            get_event_manager().post(EventMultiAttack(self, target=origin, radius=radius))
