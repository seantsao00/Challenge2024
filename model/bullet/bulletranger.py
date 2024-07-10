from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.map
import util
import view
from event_manager import EventRangedBulletDamage
from instances_manager import get_event_manager, get_model

if TYPE_CHECKING:
    from model.character import Character
    from model.team import Team
    from model.entity import LivingEntity

from model.bullet import Bullet


class BulletRanger(Bullet):
    def __init__(self, target: pg.Vector2 | tuple[float, float], position, team, attacker):
        super().__init__(position=position, entity_type=const.BulletType.RANGER,
                         team=team, speed=const.BULLET_RANGER_SPEED, attacker=attacker, damage=const.RANGER_ATTRIBUTE.ability_variables[1])
        self.target = target
        self.range = const.RANGER_ATTRIBUTE.ability_variables[0]
        self.direction = (self.target - self.position).normalize()

    def judge(self):
        """
        Move the bullet in the given direction.
        """
        original_pos = self.position
        target_pos = self.target
        if (target_pos - original_pos).length() <= self.speed and not self.hidden:
            self.hidden = True
            get_event_manager().post(EventRangedBulletDamage(bullet=self))
        else:
            self.position += self.direction*self.speed
            self.view_rotate = self.direction.angle_to(pg.Vector2(1, 0))
