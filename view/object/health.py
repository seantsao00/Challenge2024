from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import LivingEntity


class HealthView(ObjectBase):
    def __init__(self, canvas: pg.Surface, entity: LivingEntity):
        super().__init__(canvas)
        self.entity: LivingEntity = entity

    def draw(self):
        entity = self.entity
        if entity.hidden:
            return
        blood_width = (entity.health / entity.max_health) * \
            const.ENTITY_RADIUS * 2 * self.resize_ratio
        top = (self.entity.position.x - const.ENTITY_RADIUS) * self.resize_ratio
        left = (self.entity.position.y - const.ENTITY_RADIUS -
                const.HEALTH_BAR_UPPER) * self.resize_ratio
        pg.draw.rect(self.canvas, (0, 0, 0),
                     (top, left, const.ENTITY_RADIUS * 2 * self.resize_ratio, 3*self.resize_ratio))
        pg.draw.rect(self.canvas, (255, 0, 0),
                     (top, left, blood_width, 3*self.resize_ratio))
