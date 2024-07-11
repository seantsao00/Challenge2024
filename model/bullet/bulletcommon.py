from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventBulletDamage, EventBulletDisappear
from instances_manager import get_event_manager
from model.bullet.bullet import Bullet

if TYPE_CHECKING:
    from model.entity import LivingEntity
    from model.team import Team


class BulletCommon(Bullet[None]):
    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 team: Team,
                 damage: float,
                 attacker: LivingEntity,
                 speed: float,
                 victim: LivingEntity | None = None,
                 entity_type: const.EntityType = const.BulletType.COMMON):
        super().__init__(position=position, entity_type=entity_type,
                         team=team, speed=speed, attacker=attacker, damage=damage)
        self.victim = victim

    def judge(self, args: None = None):
        """
        Decide if the bullet needs to move, cause damage or disappear.
        The direction is decided by the current position of bullet and victim.
        """
        original_pos = self.position
        victim_pos = self.victim.position
        self.direction = (victim_pos - original_pos).normalize()
        if not self.victim.alive:  # The bullet needs to disappear because the victim has been dead
            get_event_manager().post(EventBulletDisappear(bullet=self))
        if (victim_pos - original_pos).length() <= self.speed:  # In the next step, the bullet would hit the victim
            get_event_manager().post(EventBulletDamage(bullet=self))
        else:  # The bullet simply moves
            self.position += self.direction*self.speed
            self.view_rotate = self.direction.angle_to(pg.Vector2(1, 0))
