from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.map
import util
import view
from event_manager import EventBulletCreate, EventBulletDisappear, EventSniperBulletDamage
from instances_manager import get_event_manager, get_model

if TYPE_CHECKING:
    from model.character import Character
    from model.team import Team
    from model.entity import LivingEntity

from model.bullet import Bullet


class BulletSniper(Bullet):
    def __init__(self, position: pg.Vector2 | tuple[float, float], entity_type: str = 'bullet',
                 speed: float = const.BULLET_SPEED, imgstate: str = 'sniper',
                 team: Team = None, victim: LivingEntity = None, damage: float = 0.0) -> None:
        super().__init__(position=position, entity_type=entity_type,
                         imgstate=imgstate, team=team, speed=speed, damage=damage)
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
            get_event_manager().post(EventSniperBulletDamage(bullet=self))
        else:
            self.position += self.direction*self.speed
