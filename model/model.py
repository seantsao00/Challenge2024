import pygame as pg

import const
import event_manager.events as events
from instances_manager import get_event_manager


class Model:
    """
    The main game engine.

    The main loop of the game is in Model.run()
    """

    def __init__(self):
        """
        This function is called when the model is created.

        For more specific objects related to a game instance,
        they should be initialized in Model.initialize()
        """
        pass

    def initialize(self, event):
        """
        This method is called when a new game is instantiated.
        """
        self.clock = pg.time.Clock()

    def handle_every_tick(self, event):
        """
        This method is called every tick.
        """
        pass

    def run(self):
        """
        The main loop of the game.
        """
        self.running = True

        # Tell every one to start
        ev_manager = get_event_manager()
        ev_manager.post(events.EventInitialize())
        self.timer = 0
        while self.running:
            ev_manager.post(events.EventEveryTick())
            self.clock.tick(const.FPS)
