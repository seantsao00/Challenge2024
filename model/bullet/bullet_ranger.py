from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventEveryTick, EventRangedBulletDamage
from instances_manager import get_event_manager, get_model
from model.bullet.bullet import Bullet

if TYPE_CHECKING:
    from model.entity import LivingEntity
    from model.team import Team


class BulletRanger(Bullet):
    def __init__(self,
                 target: pg.Vector2 | tuple[float, float],
                 position: pg.Vector2 | tuple[float, float],
                 team: Team,
                 attacker: LivingEntity):
        super().__init__(position=position, entity_type=const.BulletType.RANGER, team=team,
                         speed=const.BULLET_RANGER_SPEED, attacker=attacker,
                         damage=const.RANGER_ATTRIBUTE.ability_variables[1])
        self.target = target
        self.range = const.RANGER_ATTRIBUTE.ability_variables[0]

        self.direction = (self.target - self.position)
        self.direction = self.direction.normalize() if self.direction.length() != 0 else pg.Vector2(1, 0)

    def judge(self, _: EventEveryTick):
        """
        Decide if the bullet needs to move, cause damage or disappear.
        The direction is fixed.
        """
        original_pos = self.position
        target_pos = self.target
        model = get_model()
        if (target_pos - original_pos).length() <= self.speed * model.dt:
            get_event_manager().post(EventRangedBulletDamage(bullet=self))
        else:
            self.position += self.direction * self.speed * model.dt
            self.view_rotate = self.direction.angle_to(pg.Vector2(-1, 0))
