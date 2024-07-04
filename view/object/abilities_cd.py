from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pygame as pg

import const
from instances_manager import get_event_manager, get_model

if TYPE_CHECKING:
    from model import Character


class AbilitiesCDView:
    def __init__(self, entity: Character):
        self.entity = entity

    def draw(self, screen: pg.Surface):
        entity = self.entity
        if entity.hidden:
            return

        self.cd_width = min(get_model().get_time() - entity.abilities_time,
                            entity.abilities_cd) / entity.abilities_cd * const.ENTITY_RADIUS * 2
        pg.draw.rect(screen, (0, 0, 0),
                     (self.entity.position.x - const.ENTITY_RADIUS, self.entity.position.y - const.ENTITY_RADIUS - const.CD_BAR_UPPER, const.ENTITY_RADIUS * 2, 2))
        pg.draw.rect(screen, (0, 0, 255),
                     (self.entity.position.x - const.ENTITY_RADIUS, self.entity.position.y - const.ENTITY_RADIUS - const.CD_BAR_UPPER, self.cd_width, 2))
