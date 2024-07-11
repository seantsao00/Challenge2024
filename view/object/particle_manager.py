from __future__ import annotations

import math
import random

import pygame as pg

from const.visual.priority import PRIORITY_PARTICLE
from event_manager import EventEveryTick
from instances_manager import get_event_manager
from view.object.object_base import ObjectBase
from view.object.particle import Particle


class ParticleManager(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        self.image_initialized = True
        super().__init__(canvas, PRIORITY_PARTICLE)
        self.canvas = canvas
        self.particles = []

        get_event_manager().register_listener(EventEveryTick, self.on_every_tick)

        self.explode(pg.Vector2(200, 200), 100, 1.0, (200, 0, 0))

    def draw(self):
        for p in self.particles:
            p.draw()

    def on_every_tick(self, _: EventEveryTick):
        for p in self.particles:
            p.move()
            if p.dead:
                self.particles.remove(p)

    def explode(self, pos, amount, duration, color):
        for _ in range(amount):
            _pos = pos.copy()
            _speed = random.uniform(10, 50)
            _duration = random.uniform(0.8, 1.2) * duration
            _size = random.uniform(0.8, 1.2)
            angle = random.uniform(0, 2 * math.pi)
            _direction = pg.Vector2(math.cos(angle), math.sin(angle)).normalize()
            _color = (clamp(color[0] + random.randint(-20, 20), 0, 255),
                      clamp(color[1] + random.randint(-20, 20), 0, 255),
                      clamp(color[2] + random.randint(-20, 20), 0, 255))

            self.particles.append(Particle(self.canvas, _pos, _direction,
                                  _speed, _size, _duration, _color))


def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))
