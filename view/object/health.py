from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.tower
from const.visual.priority import PRIORITY_CD
from model import Team, Tower
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
        w, h = pg.Vector2(const.ENTITY_SIZE[entity.entity_type]
                          [entity.state]) * ScreenInfo.resize_ratio
        w, h = int(w), int(h)
        if entity.team.party is const.PartyType.NEUTRAL and isinstance(entity, Tower):
            max_health = entity.attribute.neautral_initial_health
        else:
            max_health = entity.attribute.max_health
        blood_width = (entity.health / max_health) * w
        top_left = (self.entity.position + const.HEALTH_BAR_UPPER) * \
            ScreenInfo.resize_ratio - pg.Vector2(w/2, h)
        pg.draw.rect(self.canvas, (0, 0, 0),
                     (*top_left, w, 2 * ScreenInfo.resize_ratio))
        if entity.team.party is const.PartyType.NEUTRAL:
            pg.draw.rect(self.canvas, 'red',
                         (*top_left, blood_width, 2 * ScreenInfo.resize_ratio))
        else:
            pg.draw.rect(self.canvas, const.HEALTH_BAR_COLOR[entity.team.team_id],
                         (*top_left, blood_width, 2 * ScreenInfo.resize_ratio))
