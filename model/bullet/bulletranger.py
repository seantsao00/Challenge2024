from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.map
import util
import view
from event_manager import EventBulletCreate, EventBulletDisappear, EventRangerBulletDamage
from instances_manager import get_event_manager, get_model

if TYPE_CHECKING:
    from model.character import Character
    from model.team import Team
    from model.entity import LivingEntity

from model.bullet import Bullet


class BulletRanger(Bullet):
    def __init__(self, position: pg.Vector2 | tuple[float, float], entity_type: str = 'bullet',
                 speed: float = const.BULLET_SPEED, imgstate: str = 'ranger', target: LivingEntity = None,
                 team: Team = None, range: float = 0.0, damage: float = 0.0, attacker: LivingEntity = None) -> None:
        super().__init__(position=position, entity_type=entity_type,
                         team=team, imgstate=imgstate, speed=speed, damage=damage, attacker=attacker)
        self.target = target
        self.range = range

    def judge(self):
        """
        Move the bullet in the given direction.
        """
        original_pos = self.position
        target_pos = self.target.position
        if (target_pos - original_pos).length() <= self.speed:
            get_event_manager().post(EventRangerBulletDamage(bullet=self, original_pos=original_pos))
        else:
            self.position += self.direction*self.speed
