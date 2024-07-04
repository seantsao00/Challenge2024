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


class BulletSniper(Bullet):
    def __init__(self, position: pg.Vector2 | tuple[float, float], entity_type: str = 'bullet',
                 speed: float = const.BULLET_SPEED, imgstate: str = 'default',
                 attacker: Character = None, team: Team = None, victim: Entity = None) -> None:
        super().__init__(position=position, entity_type=entity_type,
                         imgstate=imgstate, attacker=attacker, team=team, speed=speed)
        self.victim = victim

    def move(self):
        """
        Move the bullet in the given direction.
        """
        original_pos = self.position
        victim_pos = self.victim.position
        self.direction = (victim_pos - original_pos).normalize()

        if (victim_pos - original_pos).length() <= self.speed:
            get_event_manager().post(EventBulletDamage(bullet=self))
        else:
            get_event_manager().post(EventBulletMove(bullet=self, original_pos=original_pos))
