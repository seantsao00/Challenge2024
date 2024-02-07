"""
The module define the main game engine.
"""

import pygame as pg

import const
from event_manager import events
from instances_manager import get_event_manager


class Model:
    """
    The main game engine.

    The main loop of the game is in Model.run()
    """

    def __init__(self):
        """
        Initialize the Model object.

        This function is called when the model is created.
        For more specific objects related to a game instance,
        (e.g., The time that has elapsed in the game, )
        they should be initialized in Model.initialize()
        """
        pass

    def initialize(self, event: events.EventInitialize):
        """
        Initialize attributes related to a game.

        This method should be called when a new game is about to start,
        even for the second or more rounds of the game.
        """
        self.clock = pg.time.Clock()

    def handle_every_tick(self, event: events.EventEveryTick):
        """
        Do things should be done every tick.


        This method is called every tick.
        For example, if players will get point every tick, it might be done here. 
        """
        pass

    def register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(events.EventInitialize, self.initialize)
        ev_manager.register_listener(events.EventEveryTick, self.handle_every_tick)

    def run(self):
        """Run the main loop of the game."""
        self.running = True

        # Tell every one to start
        ev_manager = get_event_manager()
        ev_manager.post(events.EventInitialize())
        self.timer = 0
        while self.running:
            ev_manager.post(events.EventEveryTick())
            self.clock.tick(const.FPS)
