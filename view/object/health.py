from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.tower
from const.visual.priority import PRIORITY_CD
from model import Tower
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import LivingEntity


class HealthView(EntityObject):
    def __init__(self, canvas: pg.Surface, entity: LivingEntity):
        super().__init__(canvas, entity)
        self.priority[0] = PRIORITY_CD
        self.entity: LivingEntity

    def draw(self):
        entity = self.entity
        entity_size = const.ENTITY_SIZE[entity.entity_type][entity.state]
        if entity.team.party is const.PartyType.NEUTRAL and isinstance(entity, Tower):
            max_health = entity.attribute.neautral_initial_health
        else:
            max_health = entity.attribute.max_health
        blood_width = (entity.health / max_health) * \
            entity_size * 2 * ScreenInfo.resize_ratio
        top = (self.entity.position.x - entity_size) * ScreenInfo.resize_ratio
        left = (self.entity.position.y - entity_size -
                const.HEALTH_BAR_UPPER + const.DRAW_DISPLACEMENT_Y) * ScreenInfo.resize_ratio
        pg.draw.rect(self.canvas, (0, 0, 0),
                     (top, left, entity_size * 2 * ScreenInfo.resize_ratio, 2 * ScreenInfo.resize_ratio))
        pg.draw.rect(self.canvas, const.HEALTH_BAR_COLOR[entity.team.team_id],
                     (top, left, blood_width, 2 * ScreenInfo.resize_ratio))
