import pygame as pg

import const
from event_manager import EventMultiAttack
from instances_manager import get_event_manager
from model.character import Character


class RangerFighter(Character):
    """
    Class for the ranger fighter
    Ranger fighter has the following unique moves:
     - area_attack: Attack a locations and damage all nearby foes.
    """

    def __init__(self, team, position: pg.Vector2):
        super().__init__(position, team, const.RANGER_SPEED, const.RANGER_ATTACK_RANGE,
                         const.RANGER_DAMAGE, const.RANGER_HEALTH, const.RANGER_VISION, const.MELEE_CDTIME, const.RANGER_ABILITIES_CD)

    def abilities(self, origin: pg.Vector2, radius: float):
        dist = self.position.distance_to(origin)
        if dist <= self.attack_range:
            get_event_manager().post(EventMultiAttack(self, target=origin, radius=radius))