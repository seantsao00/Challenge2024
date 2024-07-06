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

        entity_size = const.ENTITY_SIZE[entity.entity_type][entity.state]
        cd_width = min(get_model().get_time() - entity.abilities_time, entity.ability_cd) / \
            entity.ability_cd * entity_size * 2 * self.resize_ratio
        top = (self.entity.position.x - entity_size) * self.resize_ratio
        left = (self.entity.position.y - entity_size -
                const.CD_BAR_UPPER) * self.resize_ratio
        pg.draw.rect(self.canvas, (0, 0, 0),
                     (top, left, entity_size * 2 * self.resize_ratio, 2 * self.resize_ratio))
        pg.draw.rect(self.canvas, (0, 0, 255),
                     (top, left, cd_width, 2 * self.resize_ratio))
