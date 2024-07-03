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
                         const.RANGER_DAMAGE, const.RANGER_HEALTH, const.RANGER_VISION, const.RANGER_ATTACK_SPEED, const.RANGER_ABILITIES_CD, 'ranger')
        self.abilities_radius = const.RANGER_ABILITIES_RADIUS

    def abilities(self, *args, **kwargs):
        if len(args) < 1 or not isinstance(args[0], pg.Vector2):
            raise ValueError()
        origin: pg.Vector2 = args[0]
        dist = self.position.distance_to(origin)
        if dist <= self.attack_range:
            print("ranged abilities attack")
            get_event_manager().post(EventMultiAttack(attacker=self, target=origin, radius=self.abilities_radius))
