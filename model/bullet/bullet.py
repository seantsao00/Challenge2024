from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.map
import util
import view
from event_manager import EventBulletEnd, EventBulletMove, EventBulletStart
from instances_manager import get_event_manager, get_model
from model.entity import Entity

if TYPE_CHECKING:
    from model.team import Team


class Bullet(Entity):
    def __init__(self, position: pg.Vector2 | tuple[float, float], target: Entity,
                 entity_type: str = 'bullet', imgstate: str = 'default',
                 speed: float = 0.0, is_ranged: bool = False, radius: float = None) -> None:
        super().__init__(position, entity_type=entity_type, imgstate=imgstate)
        self.direction: pg.Vector2 | tuple[float, float] = None
        self.target: Entity = target
        self.speed: float = speed
        self.is_ranged: bool = is_ranged
        self.radius: float = radius
        self.exist: bool = True

    def move(self, victim: Entity):
        """
        Move the bullet in the given direction.
        """
        original_pos = self.position
        target_pos = victim.position
        self.direction = (target_pos - original_pos).normalize()

        get_event_manager().post(EventBulletMove(bullet=self, original_pos=original_pos, victim=victim))
