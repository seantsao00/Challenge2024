from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import LivingEntity


class RangeView(ObjectBase):
    def __init__(self, canvas: pg.Vector2, entity: LivingEntity):
        super().__init__(canvas)
        self.entity: LivingEntity = entity
        self.radius: float = None
        self.color = None

    def draw(self):
        position = self.resize_ratio*self.entity.__position
        if not self.entity.__hidden:
            pg.draw.circle(self.canvas, self.color, position, self.radius, width=2)


class AttackRangeView(RangeView):
    def __init__(self, canvas: pg.Vector2, entity: LivingEntity):
        super().__init__(canvas, entity)
        self.color = const.ATTACK_RANGE_COLOR
        self.radius = (self.entity.__attack_range - 0.5) * self.resize_ratio


class ViewRangeView(RangeView):
    def __init__(self, canvas: pg.Vector2, entity: LivingEntity):
        super().__init__(canvas, entity)
        self.color = const.VIEW_RANGE_COLOR
        self.radius = (self.entity.vision + 0.5) * self.resize_ratio
