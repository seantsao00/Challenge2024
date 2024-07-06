from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from instances_manager import get_model
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import Character


class AbilitiesCDView(ObjectBase):
    def __init__(self, canvas: pg.Surface, entity: Character):
        super().__init__(canvas)
        self.entity: Character = entity

    def draw(self):
        entity = self.entity
        if entity.hidden:
            return

        cd_width = min(get_model().get_time() - entity.abilities_time, entity.ability_cd) / \
            entity.ability_cd * const.ENTITY_RADIUS * 2 * self.resize_ratio
        top = (self.entity.position.x - const.ENTITY_RADIUS) * self.resize_ratio
        left = (self.entity.position.y - const.ENTITY_RADIUS -
                const.CD_BAR_UPPER) * self.resize_ratio
        pg.draw.rect(self.canvas, (0, 0, 0),
                     (top, left, const.ENTITY_RADIUS * 2 * self.resize_ratio, 2 * self.resize_ratio))
        pg.draw.rect(self.canvas, (0, 0, 255),
                     (top, left, cd_width, 2 * self.resize_ratio))
