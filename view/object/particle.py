from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_PARTICLE
from event_manager import EventEveryTick
from instances_manager import get_event_manager, get_model
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import Particle


class ParticleView(ObjectBase):
    def __init__(self, canvas: pg.Surface, position, direction):
        self.image_initialized = True
        super().__init__(canvas, PRIORITY_PARTICLE)
        self.canvas = canvas
        self.speed: float = 100.0
        self.size: float = 1.0
        self.color: tuple = (255, 0, 0)
        self.position: pg.Vector2 = position
        self.direction: pg.Vector2 = direction
        self.duration: float = 5
        self.elapsed_time: float = 0.0

        self.event_manager = get_event_manager()
        self.model = get_model()
        self.event_manager.register_listener(EventEveryTick, self.on_every_tick)

    def draw(self):
        pg.draw.circle(self.canvas, self.color, self.position, self.size * self.resize_ratio)

    def on_every_tick(self, _: EventEveryTick):
        dt = self.model.dt
        self.position += self.direction * self.speed * dt
        self.elapsed_time += dt

        if self.elapsed_time >= self.duration:
            self.destroy()

    def destroy(self):
        self.event_manager.unregister_listener(EventEveryTick, self.on_every_tick)
