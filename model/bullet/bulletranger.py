from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.map
import util
import view
from event_manager import (EventBulletCreate, EventBulletDamage, EventBulletDisappear,
                           EventBulletMove)
from instances_manager import get_event_manager, get_model
from model.bullet import Bullet
from model.entity import Entity

if TYPE_CHECKING:
    from model.character import Character
    from model.team import Team


class BulletRanger(Bullet):
    def __init__(self, position: pg.Vector2 | tuple[float, float], entity_type: str = 'bullet',
                 speed: float = const.BULLET_SPEED, imgstate: str = 'default', target: Entity = None,
                 attacker: Character = None, team: Team = None, range: float = 0.0) -> None:
        super().__init__(position=position, entity_type=entity_type,
                         attacker=attacker, team=team, imgstate=imgstate, speed=speed)
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
