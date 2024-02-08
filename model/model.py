"""
The module defines the main game engine.
"""
import pygame as pg

import const
from event_manager import EventEveryTick, EventInitialize
from instances_manager import get_event_manager
from model.player import Player


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
        self.clock: pg.time.Clock
        self.timer: int
        self.running: bool = False
        self.state = const.State.PAUSE
        self.clock = pg.time.Clock()
        self.players: list[Player] = []
        self.register_listeners()

    def initialize(self, _: EventInitialize):
        """
        Initialize attributes related to a game.

        This method should be called when a new game is about to start,
        even for the second or more rounds of the game.
        """
        self.players = [Player(player_id) for player_id in const.PlayerIds]
        self.state = const.State.PLAY

    def handle_every_tick(self, _: EventEveryTick):
        """
        Do things should be done every tick.


        This method is called every tick.
        For example, if players will get point every tick, it might be done here. 
        """

    def register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)

    def run(self):
        """Run the main loop of the game."""
        self.running = True

        # Tell every one to start
        ev_manager = get_event_manager()
        ev_manager.post(EventInitialize())
        self.timer = 0
        while self.running:
            ev_manager.post(EventEveryTick())
            self.clock.tick(const.FPS)
