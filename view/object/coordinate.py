# view/object/coordinate.py (new file)
import pygame as pg

import const
from instances_manager import get_event_manager, get_model
from event_manager import EventShowCoordinate


class Coordinate:
    '''
    The class that handle rendering coordinate.
    '''

    def __init__(self, screen, unit: float = 0):
        self.coordinate_unit = unit  # it won't show the coordinate if the variable is set to zero
        self.register_listeners()
        self.screen = screen

    def register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventShowCoordinate, self.handle_show_coordinate)

    def handle_show_coordinate(self, event: EventShowCoordinate):
        if self.coordinate_unit == 0:
            self.coordinate_unit = event.unit
        else:
            self.coordinate_unit = 0

    def render(self):
        if self.coordinate_unit != 0:
            z = 0
            while z < const.ARENA_SIZE[0]:
                if z % 400 == 0:
                    pg.draw.line(
                        self.screen, 'gold', (z, 0), (z, const.ARENA_SIZE[1] - 1), 1
                    )
                elif z % 100 == 0:
                    pg.draw.line(
                        self.screen, 'white', (z, 0), (z, const.ARENA_SIZE[1] - 1), 1
                    )
                else:
                    pg.draw.line(
                        self.screen, 'white', (z, 0), (z, const.ARENA_SIZE[1] - 1), 1
                    )
                z += self.coordinate_unit
            z = 0
            while z < const.ARENA_SIZE[1]:
                if z % 400 == 0:
                    pg.draw.line(
                        self.screen, 'gold', (0, z), (const.ARENA_SIZE[0] - 1, z), 1
                    )
                elif z % 100 == 0:
                    pg.draw.line(
                        self.screen, 'white', (0, z), (const.ARENA_SIZE[0] - 1, z), 1
                    )
                else:
                    pg.draw.line(
                        self.screen, 'white', (0, z), (const.ARENA_SIZE[0] - 1, z), 1
                    )
                z += self.coordinate_unit
