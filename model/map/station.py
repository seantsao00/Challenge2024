"""
This file is defined specially for map station (train station). It handles how the vehicles should be spawned.
Currently, there is no prorotype defined for special map handling, but this should be abstracted.
"""
import random
from enum import Enum

import pygame as pg

import const
from event_manager import EventEveryTick
from instances_manager import get_event_manager, get_model
from model.vehicle import Vehicle
from util import log_info


class SpecialMapStation():
    class Spots(Enum):
        UP_LEFT = pg.Vector2(69.5, 0), const.VehicleState.FRONT
        UP_RIGHT = pg.Vector2(165.5, 0), const.VehicleState.FRONT
        LEFT_UP = pg.Vector2(0, 82.5), const.VehicleState.RIGHT
        LEFT_DOWN = pg.Vector2(0, 178.5), const.VehicleState.RIGHT
        DOWN_LEFT = pg.Vector2(82.5, 249), const.VehicleState.BACK
        DOWN_RIGHT = pg.Vector2(178.5, 249), const.VehicleState.BACK
        RIGHT_UP = pg.Vector2(249, 69.5), const.VehicleState.LEFT
        RIGHT_DOWN = pg.Vector2(249, 165.5), const.VehicleState.LEFT

    def __init__(self):
        self.generation_sequence: list[tuple[float, pg.Vector2, const.VehicleState]] = []
        self.idx = 0
        self.rng = random.Random()
        # Phase 1: 10 seconds of grace period
        # Phase 2: 20 seconds of traffic
        self.generate_traffic(10, 30, rate=2)
        # Phase 3: 30 second of occational vehicle
        self.generate_traffic(30, 60, rate=0.5)
        # Phase 4: 30 seconds of high density traffic
        self.generate_traffic(60, 90, rate=1)
        # Phase 5: 90 seconds of increasingly heavy traffic
        self.generate_traffic(90, 120, rate=0.25)
        self.generate_traffic(120, 135, rate=0.5)
        self.generate_traffic(135, 150, rate=2)
        self.generate_traffic(150, 165, rate=4)
        self.generate_traffic(165, 180, rate=7)
        self.generation_sequence.sort(key=lambda x: x[0])
        get_event_manager().register_listener(EventEveryTick, self.handle_every_tick)
        log_info("Loaded map 'station' special handling.")

    def generate_traffic(self, start: float, end: float, rate: float):
        # Average `rate` car per second
        for _ in range(int((end - start) * rate)):
            position, state = self.rng.choice([e.value for e in SpecialMapStation.Spots])
            self.generation_sequence.append((self.rng.uniform(start, end), position, state))

    def handle_every_tick(self, _: EventEveryTick):
        time_now = get_model().get_time()
        while (self.idx < len(self.generation_sequence) and
               time_now >= self.generation_sequence[self.idx][0]):
            Vehicle(self.generation_sequence[self.idx][1],
                    get_model().neutral_team,
                    self.generation_sequence[self.idx][2])
            self.idx += 1
