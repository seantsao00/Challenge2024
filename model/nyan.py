import pygame as pg

import const
from event_manager import EventEveryTick, EventNyanCat
from instances_manager import get_event_manager


class Nyan:
    def __init__(self):
        self.enabled = False
        self.position = pg.Vector2(500, 220)
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventEveryTick, self.move)
        ev_manager.register_listener(EventNyanCat, self.activate)

    def activate(self, _: EventNyanCat):
        self.enabled = True
        self.position = pg.Vector2(500, 220)

    def deactivate(self):
        self.enabled = False

    def move(self, _: EventEveryTick):
        if self.enabled:
            self.position.x -= 2
            if self.position.x < -200:
                self.deactivate()
