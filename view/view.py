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
        self.screen = pg.display.set_mode(size=const.WINDOW_SIZE)
        pg.display.set_caption(const.WINDOW_CAPTION)
        PlayerView.init_convert()
        self.register_listeners()

    def initialize(self, _: EventInitialize):
        """
        Initialize components that require initialization at the start of every game.
        """

    def handle_every_tick(self, _: EventEveryTick):
        self.display_fps()
        self.screen.fill(const.BACKGROUND_COLOR)
        model = get_model()
        for en in model.entities:
            en.view.draw(self.screen)
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
