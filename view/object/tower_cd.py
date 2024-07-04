from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pygame as pg

import const

if TYPE_CHECKING:
    from model import LivingEntity


class TowerCDView:
    def __init__(self, entity: LivingEntity):
        self.entity = entity

    def draw(self, screen: pg.Surface):
        entity = self.entity
        if entity.hidden or entity.spawn_timer is None:
            return

        self.cd_width = (entity.spawn_timer.interval - entity.spawn_timer.get_remaining_time()
                         ) / entity.spawn_timer.interval * const.ENTITY_RADIUS * 2
        pg.draw.rect(screen, (0, 0, 0),
                     (self.entity.position.x - const.ENTITY_RADIUS, self.entity.position.y - const.ENTITY_RADIUS - const.CD_BAR_UPPER, const.ENTITY_RADIUS * 2, 2))
        pg.draw.rect(screen, (0, 0, 255),
                     (self.entity.position.x - const.ENTITY_RADIUS, self.entity.position.y - const.ENTITY_RADIUS - const.CD_BAR_UPPER, self.cd_width, 2))
