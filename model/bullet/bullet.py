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
                 speed: float = 0.0, imgstate: str = 'default', team: Team = None) -> None:
        super().__init__(position, entity_type=entity_type, imgstate=imgstate, team=team)
        self.direction: pg.Vector2 | tuple[float, float] = None
        self.speed: float = speed
        self.exist: bool = True
