from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_CD
from view.object.entity_object import EntityObject

if TYPE_CHECKING:
    from model import LivingEntity


class HealthView(EntityObject):
    def __init__(self, canvas: pg.Surface, entity: LivingEntity):
        super().__init__(canvas, entity)
        self.priority[0] = PRIORITY_CD
        self.entity: LivingEntity

    def draw(self):
        entity = self.entity
        entity_size = const.ENTITY_SIZE[entity.entity_type][entity.state]
        blood_width = (entity.health / entity.attribute.max_health) * \
            entity_size * 2 * self.resize_ratio
        top = (self.entity.position.x - entity_size) * self.resize_ratio
        left = (self.entity.position.y - entity_size -
                const.HEALTH_BAR_UPPER + const.DRAW_DISPLACEMENT_Y) * self.resize_ratio
        pg.draw.rect(self.canvas, (0, 0, 0),
                     (top, left, entity_size * 2 * self.resize_ratio, 2 * self.resize_ratio))
        pg.draw.rect(self.canvas, (255, 0, 0),
                     (top, left, blood_width, 2 * self.resize_ratio))
