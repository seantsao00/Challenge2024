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
    def __init__(self, position: pg.Vector2 | tuple[float, float], direction: pg.Vector2 | tuple[float, float],
                 entity_type: str = 'bullet', team: Team = None, imgstate: str = 'default',
                 speed: float = 0.0) -> None:
        super().__init__(position, entity_type=entity_type, team=team, imgstate=imgstate)
        self.direction: pg.Vector2 | tuple[float, float] = direction
        self.speed: float = speed
        self.exist: bool = True

    def move(self, victim: Entity):
        """
        Move the bullet in the given direction.
        """
        original_pos = self.position
        target_pos = victim.position
        self.direction = (target_pos - original_pos).normalize()

        get_event_manager().post(EventBulletMove(bullet=self, original_pos=original_pos, victim=victim))
