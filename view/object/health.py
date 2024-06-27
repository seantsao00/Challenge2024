from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const

if TYPE_CHECKING:
    from model import Character


class HealthView:

    def __init__(self, character: Character):
        self.character = character

    def draw(self, screen: pg.Surface):
        character = self.character
        if character.hidden:
            return
        blood_width = (character.health / character.max_health) * const.ENTITY_RADIUS * 2
        pg.draw.rect(screen, (0, 0, 0),
                     (self.character.position.x - const.ENTITY_RADIUS, self.character.position.y - 2 * const.ENTITY_RADIUS - 8, const.ENTITY_RADIUS * 2, 3))
        pg.draw.rect(screen, (255, 0, 0),
                     (self.character.position.x - const.ENTITY_RADIUS, self.character.position.y - 2 * const.ENTITY_RADIUS - 8, blood_width, 3))
