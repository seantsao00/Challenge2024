from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

import const
from model.entity import Entity

if TYPE_CHECKING:
    import pygame as pg

    from model.entity import LivingEntity
    from model.team import Team


class Bullet(Entity):
    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 entity_type: const.BulletType,
                 team: Team | None = None,
                 speed: float = 0.0,
                 damage: float = 0.0,
                 attacker: LivingEntity = None):
        self.view_rotate: float = 0.0
        self.direction: pg.Vector2 | tuple[float, float] | None = None
        self.speed: float = speed
        self.damage: float = damage
        self.attacker: LivingEntity = attacker

        super().__init__(position=position, entity_type=entity_type, team=team)

    @abstractmethod
    def judge(self):
        pass
