from __future__ import annotations

from math import pi
from typing import TYPE_CHECKING

import pygame as pg

import const
from view.object.entity_object import EntityObject

if TYPE_CHECKING:
    from model import Tower


class TowerCDView(EntityObject):
    def __init__(self, canvas: pg.Vector2, entity: Tower):
        super().__init__(canvas, entity)
        self.entity: Tower

    def draw(self):
        entity = self.entity
        if entity.hidden or entity.spawn_timer is None:
            return

        entity_size = const.ENTITY_SIZE[entity.entity_type][entity.state]
        radius = entity_size / 1.5 * self.resize_ratio
        position = self.resize_ratio * (entity.position + pg.Vector2(entity_size, entity_size))
        pg.draw.circle(self.canvas, 'black', position, radius, width=int(3*self.resize_ratio))
        cd_remaining = (entity.spawn_timer.interval -
                        entity.spawn_timer.get_remaining_time()) / entity.spawn_timer.interval
        pg.draw.arc(self.canvas, const.CD_BAR_COLOR, pg.Rect((self.resize_ratio*entity.position + pg.Vector2(self.resize_ratio*entity_size - radius,
                    self.resize_ratio*entity_size - radius)), pg.Vector2(radius*2, radius*2)), pi / 2, pi / 2 - pi * 2 * cd_remaining, width=int(3*self.resize_ratio))
