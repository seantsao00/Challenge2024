from typing import Iterable

import pygame as pg

from view.object.object_base import ObjectBase


class BackgroundObject(ObjectBase):
    def __init__(self, canvas: pg.Surface, priority: Iterable[float], render_position: pg.Vector2 | tuple[float, float], image: pg.Surface):
        super().__init__(canvas, priority)
        self.render_position = render_position
        self.image = image

    def draw(self):
        self.canvas.blit(self.image, self.render_position)
