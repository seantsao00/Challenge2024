from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

import const
from model.entity import Entity

if TYPE_CHECKING:
    import pygame as pg

    from model.entity import LivingEntity
    from model.team import Team

T = TypeVar('T')


class Bullet(Entity, Generic[T]):
    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 entity_type: const.BulletType,
                 team: Team = None,
                 speed: float = 0.0,
                 damage: float = 0.0,
                 attacker: LivingEntity = None):
        super().__init__(position=position, entity_type=entity_type, team=team, state=const.BulletState.FLYING)
        self.direction: pg.Vector2 | tuple[float, float] | None = None
        self.speed: float = speed
        self.damage: float = damage
        self.attacker: LivingEntity = attacker
        self.view_rotate: float = 0.0

    @abstractmethod
    def judge(self, args: T):
        pass
