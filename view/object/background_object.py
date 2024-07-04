from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import LivingEntity


class BackGroundObject(ObjectBase):
    def __init__(self, canvas: pg.Surface, height: float, render_position: pg.Vector2 | tuple[float, float], image: pg.Surface):
        super().__init__(canvas, 1, height)
        self.render_position = render_position
        self.image = image

    def draw(self):
        self.canvas.blit(self.image, self.render_position)
