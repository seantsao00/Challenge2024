from __future__ import annotations

from math import pi
from typing import TYPE_CHECKING

import pygame as pg

import const
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import LivingEntity


class TowerCDView(ObjectBase):
    def __init__(self, canvas: pg.Vector2, ratio: float, entity: LivingEntity):
        super().__init__(canvas, ratio)
        self.entity: LivingEntity = entity

    def draw(self):
        entity = self.entity
        if entity.hidden or entity.spawn_timer is None:
            return

        radius = const.ENTITY_RADIUS / 1.5
        pg.draw.circle(self.canvas, 'black', entity.position +
                       pg.Vector2(const.ENTITY_RADIUS, const.ENTITY_RADIUS), radius, width=3)
        cd_remaining = (entity.spawn_timer.interval -
                        entity.spawn_timer.get_remaining_time()) / entity.spawn_timer.interval
        pg.draw.arc(self.canvas, const.CD_BAR_COLOR, pg.Rect(entity.position + pg.Vector2(const.ENTITY_RADIUS - radius,
                    const.ENTITY_RADIUS - radius), pg.Vector2(radius*2, radius*2)), pi / 2, pi / 2 - pi * 2 * cd_remaining, width=3)
