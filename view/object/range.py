from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from instances_manager import get_model
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import LivingEntity


class RangeView(EntityObject):
    def __init__(self, canvas: pg.Vector2, entity: LivingEntity):
        super().__init__(canvas, entity)
        self.entity: LivingEntity
        self.radius: float = None
        self.color = None

    def draw(self):
        model = get_model()
        if model.show_range:
            position = ScreenInfo.resize_ratio*self.entity.position
            pg.draw.circle(self.canvas, self.color, position, self.radius, width=2)


class AttackRangeView(RangeView):
    def __init__(self, canvas: pg.Vector2, entity: LivingEntity):
        super().__init__(canvas, entity)
        self.color = const.ATTACK_RANGE_COLOR
        self.radius = (self.entity.attribute.attack_range - 0.5) * ScreenInfo.resize_ratio


class ViewRangeView(RangeView):
    def __init__(self, canvas: pg.Vector2, entity: LivingEntity):
        super().__init__(canvas, entity)
        self.color = const.VIEW_RANGE_COLOR
        self.radius = (self.entity.attribute.vision + 0.5) * ScreenInfo.resize_ratio
