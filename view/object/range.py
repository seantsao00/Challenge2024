from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const

if TYPE_CHECKING:
    from model import Entity
    from model.character import Character


class RangeView:
    def __init__(self, character: Character):
        self.character: Character = character
        self.radius: float = None
        self.color = None

    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.character.position, self.radius, width=1)


class AttackRangeView(RangeView):
    def __init__(self, character: Character):
        super().__init__(character)
        self.color = const.ATTACK_RANGE_COLOR
        self.radius = self.character.attack_range - 0.5


class ViewRangeView(RangeView):
    def __init__(self, character: Character):
        super().__init__(character)
        self.color = const.VIEW_RANGE_COLOR
        self.radius = self.character.vision + 0.5
