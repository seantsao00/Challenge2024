from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import (EventBulletDamage, EventBulletDisappear, EventEveryTick,
                           EventSniperBulletParticle)
from instances_manager import get_event_manager, get_model
from model.bullet.bullet import Bullet

if TYPE_CHECKING:
    from model.entity import LivingEntity
    from model.team import Team


class BulletCommon(Bullet):
    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 team: Team,
                 damage: float,
                 attacker: LivingEntity,
                 speed: float,
                 victim: LivingEntity | None = None,
                 entity_type: const.EntityType = const.BulletType.COMMON,
                 is_sniper_ability: bool = False):
        super().__init__(position=position, entity_type=entity_type,
                         team=team, speed=speed, attacker=attacker, damage=damage)
        self.victim = victim
        self.is_sniper_ability = is_sniper_ability
        self.particle_dt: float = 0

    def judge(self, _: EventEveryTick):
        """
        Decide if the bullet needs to move, cause damage or disappear.
        The direction is decided by the current position of bullet and victim.
        """
        original_pos = self.position
        victim_pos = self.victim.position
        model = get_model()
        ev_manager = get_event_manager()
        if not self.victim.alive:
            ev_manager.post(EventBulletDisappear(bullet=self))
        elif (victim_pos - original_pos).length() <= self.speed * model.dt:
            ev_manager.post(EventBulletDamage(bullet=self))
        else:
            self.direction = (victim_pos - original_pos).normalize()
            self.position += self.direction * self.speed * model.dt
            self.view_rotate = self.direction.angle_to(pg.Vector2(-1, 0))
            self.particle_dt += model.dt
            if self.is_sniper_ability and self.particle_dt >= const.BULLET_SNIPER_PARTICLE_DT:
                self.particle_dt %= const.BULLET_SNIPER_PARTICLE_DT
                ev_manager.post(EventSniperBulletParticle(bullet=self))
