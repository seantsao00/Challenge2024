from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.map
import util
import view
from event_manager import EventBulletDamage, EventBulletEnd, EventBulletMove, EventBulletStart
from instances_manager import get_event_manager, get_model
from model.entity import Entity

if TYPE_CHECKING:
    from model.team import Team


class Bullet(Entity):
    def __init__(self, position: pg.Vector2 | tuple[float, float], entity_type: str = 'bullet',
                 speed: float = 0.0, imgstate: str = 'default') -> None:
        super().__init__(position, entity_type=entity_type, imgstate=imgstate)
        self.direction: pg.Vector2 | tuple[float, float] = None
        self.speed: float = speed
        self.exist: bool = True


class BulletSniper(Bullet):
    def __init__(self, position: pg.Vector2 | tuple[float, float], entity_type: str = 'bullet',
                 speed: float = 0.0, imgstate: str = 'default', victim: Entity = None) -> None:
        super().__init__(position=position, entity_type=entity_type, imgstate=imgstate, speed=speed)
        self.victim = victim

    def move(self):
        """
        Move the bullet in the given direction.
        """
        original_pos = self.position
        victim_pos = self.victim.position
        self.direction = (victim_pos - original_pos).normalize()

        if (victim_pos - original_pos).length() <= self.speed:
            get_event_manager().post(EventBulletDamage(bullet=self, original_pos=original_pos, victim=self.victim))
        else:
            get_event_manager().post(EventBulletMove(bullet=self, original_pos=original_pos, victim=self.victim))


class BulletRanger(Bullet):
    def __init__(self, position: pg.Vector2 | tuple[float, float], entity_type: str = 'bullet',
                 speed: float = 0.0, imgstate: str = 'default', target: Entity = None, range: float = 0.0) -> None:
        super().__init__(position=position, entity_type=entity_type, imgstate=imgstate, speed=speed)
        self.target = target
        self.range = range

    def move(self):
        """
        Move the bullet in the given direction.
        """
        original_pos = self.position
        target_pos = self.target.position
        if (target_pos - original_pos).length() <= self.speed:
            get_event_manager().post(EventBulletDamage(bullet=self, original_pos=original_pos, target=self.target))
        else:
            get_event_manager().post(EventBulletMove(bullet=self, original_pos=original_pos, target=self.target))
