"""
The module defines View class.
"""

import pygame as pg

import const
from event_manager import EventEveryTick, EventInitialize, EventPlayerMove, EventQuit
from instances_manager import get_event_manager, get_model
from view.object import EntityView, ObjectBase, PlayerView


class View:
    """
    The class that presents the actual game content on the screen.
    """

    def __init__(self):
        """
        Initialize the View instance upon its creation.

        For more specific objects related to a game instance, 
        they should be initialized in View.initialize().
        """
        size = pg.display.Info()
        self.canvas = pg.display.set_mode(size=const.WINDOW_SIZE, flags=pg.RESIZABLE|pg.DOUBLEBUF).copy()
        self.screen = pg.display.set_mode(size=(size.current_w, size.current_h), flags=pg.RESIZABLE|pg.DOUBLEBUF)
        # print(self.canvas.get_rect().size)
        # print(self.screen.get_rect().size)
        pg.display.set_caption(const.WINDOW_CAPTION)
        PlayerView.init_convert()
        self.register_listeners()

    def initialize(self, _: EventInitialize):
        """
        Initialize components that require initialization at the start of every game.
        """

    def handle_every_tick(self, _: EventEveryTick):
        self.display_fps()
        self.canvas.fill(const.BACKGROUND_COLOR)
        model = get_model()
        for en in model.entities:
            en.view.draw(self.canvas)

        # For test
        pg.draw.line(
            self.canvas, 'white', (const.ARENA_SIZE[0], 0), (const.ARENA_SIZE[0], const.ARENA_SIZE[1] - 1), 1
        )
        self.screen.blit(pg.transform.scale(self.canvas, self.screen.get_rect().size), (0, 0))
        pg.display.flip()

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)

    def display_fps(self):
        """Display the current fps on the window caption."""
        model = get_model()
        pg.display.set_caption(
            f'{const.WINDOW_CAPTION} - FPS: {model.clock.get_fps():.2f}')
