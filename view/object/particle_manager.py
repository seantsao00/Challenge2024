from __future__ import annotations

import math
import random

import pygame as pg

import const
from event_manager import EventBulletExplode, EventEveryTick
from instances_manager import get_event_manager
from view.object.object_base import ObjectBase
from view.object.particle import Particle
from view.screen_info import ScreenInfo


class ParticleManager(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        self.image_initialized = True
        super().__init__(canvas, const.PRIORITY_PARTICLE)
        self.canvas = canvas
        self.particles = []

        self.register_events()

    def register_events(self):
        ev_manager = get_event_manager()
        get_event_manager().register_listener(EventEveryTick, self.on_every_tick)
        ev_manager.register_listener(EventBulletExplode, self.bullet_explode)

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
            _pos = pos * ScreenInfo.resize_ratio
            _speed = random.uniform(40, 60)
            _duration = random.uniform(0.8, 1.2) * duration
            _size = random.uniform(0.8, 1.2)
            angle = random.uniform(0, 2 * math.pi)
            _direction = pg.Vector2(math.cos(angle), math.sin(angle)).normalize()
            _color = (clamp(color[0] + random.randint(-20, 20), 0, 255),
                      clamp(color[1] + random.randint(-20, 20), 0, 255),
                      clamp(color[2] + random.randint(-20, 20), 0, 255))

            self.particles.append(Particle(self.canvas, _pos, _direction,
                                  _speed, _size, _duration, _color))

    def blood(self, pos, amount, duration):
        color = (200, 0, 0)
        for _ in range(amount):
            _pos = pos + pg.Vector2(random.randint(-7, 7), 0)
            _speed = random.uniform(50, 100)
            _duration = random.uniform(0.8, 1.2) * duration
            _size = random.uniform(0.8, 1.2)
            _direction = pg.Vector2(0, 1)
            _color = (clamp(color[0] + random.randint(-20, 20), 0, 255),
                      clamp(color[1] + random.randint(-20, 20), 0, 255),
                      clamp(color[2] + random.randint(-20, 20), 0, 255))

            self.particles.append(Particle(self.canvas, _pos, _direction,
                                  _speed, _size, _duration, _color))

    def bullet_explode(self, event: EventBulletExplode):
        self.explode(event.bullet.position, const.PARTICLES_BULLET_EXPLODE_AMOUNT,
                     const.PARTICLES_BULLET_EXPLODE_DURATION, const.PARTICLES_BULLET_EXPLODE_COLOR)


def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))
