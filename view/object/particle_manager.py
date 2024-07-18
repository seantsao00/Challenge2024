from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventBulletExplode, EventEveryTick, EventSniperBulletParticle
from instances_manager import get_event_manager
from util import clamp
from view.object.particle import Particle
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Team


class ParticleManager:
    def __init__(self, canvas: pg.Surface):
        self.__canvas = canvas
        self.__particles: set[Particle] = set()
        self.__rng = random.Random()
        """Random number generator. This is used to patch potential RNG manipulation."""
        self.__register_listeners()

    def __handle_event_every_tick(self, _: EventEveryTick):
        wait_remove = set()
        for p in self.__particles:
            p.move()
            if p.dead:
                wait_remove.add(p)
        self.__particles.difference_update(wait_remove)

    def __explode(self, pos, amount, duration, color, speed, size):
        """Accept arena coordinate."""
        for _ in range(amount):
            _pos = (pos * ScreenInfo.resize_ratio
                    + pg.Vector2((ScreenInfo.screen_size[0] - ScreenInfo.screen_size[1]) / 2, 0))
            # print(_pos)
            _speed = self.__rng.uniform(20, 60) * speed
            _duration = self.__rng.uniform(1, 1.4) * duration
            _size = self.__rng.uniform(0.8, 1.2) * size
            angle = self.__rng.uniform(0, 2 * math.pi)
            _direction = pg.Vector2(math.cos(angle), math.sin(angle)).normalize()
            _color = (clamp(color[0] + self.__rng.randint(-20, 20), 0, 255),
                      clamp(color[1] + self.__rng.randint(-20, 20), 0, 255),
                      clamp(color[2] + self.__rng.randint(-20, 20), 0, 255))

            self.__particles.add(Particle(self.__canvas, pos, _pos, _direction,
                                          _speed, _size, _duration, _color))

    def __handle_bullet_explode(self, event: EventBulletExplode):
        self.__explode(event.bullet.position, const.PARTICLES_BULLET_EXPLODE_AMOUNT,
                       const.PARTICLES_BULLET_EXPLODE_DURATION, const.HEALTH_BAR_COLOR[event.bullet.team.team_id],
                       const.PARTICLES_BULLET_EXPLODE_SPEED, const.PARTICLE_BULLET_EXPLODE_SIZE)

    def __handle_sniper_bullet(self, event: EventSniperBulletParticle):
        self.__explode(event.bullet.position, const.PARTICLES_BULLET_MOVE_AMOUNT,
                       const.PARTICLES_BULLET_MOVE_DURATION, const.HEALTH_BAR_COLOR[event.bullet.team.team_id],
                       const.PARTICLES_BULLET_MOVE_SPEED, const.PARTICLE_BULLET_MOVE_SIZE)

    def __register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventEveryTick, self.__handle_event_every_tick)
        ev_manager.register_listener(EventBulletExplode, self.__handle_bullet_explode)
        ev_manager.register_listener(EventSniperBulletParticle, self.__handle_sniper_bullet)

    def blood(self, pos, amount, duration):
        color = (200, 0, 0)
        for _ in range(amount):
            _pos = pos + pg.Vector2(self.__rng.randint(-7, 7), 0)
            _speed = self.__rng.uniform(50, 100)
            _duration = self.__rng.uniform(0.8, 1.2) * duration
            _size = self.__rng.uniform(0.8, 1.2)
            _direction = pg.Vector2(0, 1)
            _color = (clamp(color[0] + self.__rng.randint(-20, 20), 0, 255),
                      clamp(color[1] + self.__rng.randint(-20, 20), 0, 255),
                      clamp(color[2] + self.__rng.randint(-20, 20), 0, 255))

            self.__particles.add(Particle(self.__canvas, pos, _pos, _direction,
                                          _speed, _size, _duration, _color))

    def draw(self, check_vision: bool = False, team: Team | None = None):
        for p in self.__particles:
            if not check_vision:
                p.draw()
            elif check_vision and team.vision.entity_inside_vision(p):
                p.draw()
