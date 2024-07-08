from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import util
import view
from event_manager import EventBulletDisappear, EventBulletDamage
from instances_manager import get_event_manager, get_model

if TYPE_CHECKING:
    from model.character import Character
    from model.team import Team
    from model.entity import LivingEntity

from model.bullet import Bullet


class BulletCommon(Bullet):
    def __init__(self, position, team, damage, attacker, speed, victim: LivingEntity = None):
        super().__init__(position=position, team=team, speed=speed, attacker=attacker, damage=damage)
        self.victim = victim

    def judge(self):
        """
        Move the bullet in the given direction.
        """
        original_pos = self.position
        victim_pos = self.victim.position
        self.direction = (victim_pos - original_pos).normalize()
        if hasattr(self.victim, 'alive') and self.victim.alive == False:
            get_event_manager().post(EventBulletDisappear(bullet=self))
        if (victim_pos - original_pos).length() <= self.speed:
            get_event_manager().post(EventBulletDamage(bullet=self))
        else:
            self.position += self.direction*self.speed
