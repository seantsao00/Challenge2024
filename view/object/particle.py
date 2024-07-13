from __future__ import annotations

import pygame as pg

from const.visual.priority import PRIORITY_PARTICLE
from instances_manager import get_model
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo


class Particle(ObjectBase):
    def __init__(self, canvas: pg.Surface, position: pg.Vector2, direction: pg.Vector2,
                 speed: float, size: float, duration: float, color: pg.Color):
        self.image_initialized = True
        super().__init__(canvas, [PRIORITY_PARTICLE])
        self.canvas = canvas
        self.speed = speed
        self.size = size
        self.color = color
        self.position = position
        self.direction = direction
        self.duration = duration
        self.elapsed_time: float = 0.0
        self.dead = False

    def draw(self):
        pg.draw.circle(self.canvas, self.color, self.position, self.size * ScreenInfo.resize_ratio)

    def move(self):
        dt = get_model().dt
        self.position += self.direction * self.speed * dt
        self.elapsed_time += dt

        if self.elapsed_time >= self.duration:
            self.dead = True
