from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const

if TYPE_CHECKING:
    from model import Entity


class RangeView:
    def __init__(self, entity: Entity):
        self.entity: Entity = entity
        self.radius: float = None
        self.color = None

    def draw(self, screen):
        if not self.entity.hidden:
            pg.draw.circle(screen, self.color, self.entity.position, self.radius, width=1)


class AttackRangeView(RangeView):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self.color = const.ATTACK_RANGE_COLOR
        self.radius = self.entity.attack_range - 0.5


class ViewRangeView(RangeView):
    def __init__(self, entity: Entity):
        super().__init__(entity)
        self.color = const.VIEW_RANGE_COLOR
        self.radius = self.entity.vision + 0.5
