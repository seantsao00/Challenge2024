from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from instances_manager import get_model
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import Character


class AbilitiesCDView(ObjectBase):
    def __init__(self, canvas: pg.Surface, ratio: float, entity: Character):
        super().__init__(canvas, ratio)
        self.entity: Character = entity

    def draw(self):
        entity = self.entity
        if entity.hidden:
            return

        cd_width = min(get_model().get_time() - entity.abilities_time,
                       entity.abilities_cd) / entity.abilities_cd * const.ENTITY_RADIUS * 2
        pg.draw.rect(self.canvas, (0, 0, 0),
                     (self.entity.position.x - const.ENTITY_RADIUS, self.entity.position.y - const.ENTITY_RADIUS - const.CD_BAR_UPPER, const.ENTITY_RADIUS * 2, 2))
        pg.draw.rect(self.canvas, (0, 0, 255),
                     (self.entity.position.x - const.ENTITY_RADIUS, self.entity.position.y - const.ENTITY_RADIUS - const.CD_BAR_UPPER, cd_width, 2))
