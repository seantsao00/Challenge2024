from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import LivingEntity


class RangeView(ObjectBase):
    def __init__(self, canvas: pg.Vector2, ratio: float, entity: LivingEntity):
        super().__init__(canvas, ratio)
        self.entity: LivingEntity = entity
        self.radius: float = None
        self.color = None

    def draw(self):
        if not self.entity.hidden:
            pg.draw.circle(self.canvas, self.color, self.entity.position, self.radius, width=1)


class AttackRangeView(RangeView):
    def __init__(self, canvas: pg.Vector2, ratio: float, entity: LivingEntity):
        super().__init__(canvas, ratio, entity)
        self.color = const.ATTACK_RANGE_COLOR
        self.radius = self.entity.attack_range - 0.5


class ViewRangeView(RangeView):
    def __init__(self, canvas: pg.Vector2, ratio: float, entity: LivingEntity):
        super().__init__(canvas, ratio, entity)
        self.color = const.VIEW_RANGE_COLOR
        self.radius = self.entity.vision + 0.5
