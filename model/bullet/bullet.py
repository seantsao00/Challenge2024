from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import util
import view
from instances_manager import get_event_manager, get_model
from model.entity import Entity, LivingEntity
from model.timer import Timer

if TYPE_CHECKING:
    from model.character import Character
    from model.team import Team


class Bullet(Entity):
    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 entity_type: const.BulletType,
                 team: Team = None,
                 speed: float = 0.0,
                 damage: float = 0.0,
                 attacker: LivingEntity = None):
        super().__init__(position=position, entity_type=entity_type, team=team)
        self.direction: pg.Vector2 | tuple[float, float] = None
        self.speed: float = speed
        self.damage: float = damage
        self.timer: Timer = None
        self.attacker: LivingEntity = attacker
        self.view_rotate: float = 0

    def judge(self, *args, **kwargs):
        pass
