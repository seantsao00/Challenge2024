from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from instances_manager import get_model
from view.object.entity_object import EntityObject

if TYPE_CHECKING:
    from model import Character


class AbilitiesCDView(EntityObject):
    def __init__(self, canvas: pg.Surface, entity: Character):
        super().__init__(canvas, entity)
        self.entity: Character
        self.register_listeners()

    def draw(self):
        entity = self.entity
        entity_size = const.ENTITY_SIZE[entity.entity_type][entity.state]
        cd_width = min(max(get_model().get_time() - entity.abilities_time, 0), entity.attribute.ability_cd) / \
            entity.attribute.ability_cd * entity_size * 2 * self.resize_ratio
        top = (self.entity.position.x - entity_size) * self.resize_ratio
        left = (self.entity.position.y - entity_size -
                const.CD_BAR_UPPER + const.DRAW_DISPLACEMENT_Y) * self.resize_ratio
        pg.draw.rect(self.canvas, (0, 0, 0),
                     (top, left, entity_size * 2 * self.resize_ratio, 2 * self.resize_ratio))
        pg.draw.rect(self.canvas, (0, 0, 255),
                     (top, left, cd_width, 2 * self.resize_ratio))
