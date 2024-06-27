from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from util import crop_image
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import Entity
    from model import Character
    from model import Tower


class HealthView:

    def __init__(self, entity: Entity | Character | Tower):
        self.entity = entity

    def draw(self, screen: pg.Surface):
        entity = self.entity
        if entity.hidden == True:
            return
        blood_width = (entity.health / entity.max_health) * const.ENTITY_RADIUS * 2
        pg.draw.rect(screen, (0, 0, 0),
                     (self.entity.position.x - const.ENTITY_RADIUS, self.entity.position.y - const.ENTITY_RADIUS - const.HEALTH_BAR_UPPER, const.ENTITY_RADIUS * 2, 3))
        pg.draw.rect(screen, (255, 0, 0),
                     (self.entity.position.x - const.ENTITY_RADIUS, self.entity.position.y - const.ENTITY_RADIUS - const.HEALTH_BAR_UPPER, blood_width, 3))
