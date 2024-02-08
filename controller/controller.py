"""
The module defines Controller class.
"""
import pygame as pg

import const
from event_manager import EventEveryTick, EventInitialize, EventPlayerMove, EventQuit
from instances_manager import get_event_manager, get_model


class Controller:
    """
    The object handles the control input, either from keyboard or from AI.
    """

    def __init__(self):
        """
        Initialize the Controller object.

        This function is called when the Controller is created.
        For more specific objects related to a game instance,
        they should be initialized in Controller.initialize()
        """
        self.register_listeners()

    def initialize(self, _: EventInitialize):
        """Initialize attributes related to a game."""

    def handle_every_tick(self, _: EventEveryTick):
        """Do things should be done every tick."""
        key_down_events = []
        ev_manager = get_event_manager()
        model = get_model()
        # Called once per game tick. We check our keyboard presses here.
        for event_pg in pg.event.get():
            # handle window manager closing our window
            if event_pg.type == pg.QUIT:
                ev_manager.post(EventQuit())
            if event_pg.type == pg.KEYDOWN:
                key_down_events.append(event_pg)
            # for orientating
            if event_pg.type == pg.MOUSEBUTTONDOWN:
                if event_pg.button == 1:  # Left mouse button
                    mouse_pos = event_pg.pos
                    x, y = mouse_pos
                    print(f"Mouse click position: ({x}, {y})")

        cur_state = model.state
        if cur_state == const.State.PLAY:
            self.ctrl_play()

    def register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)

    def ctrl_play(self):
        """
        Control the behavior of player characters depending on key input during the game.

        When the method called, controller get what keys is pressed in this tick,
        and post EventPlayerMove according to the keys pressed.
        """
        ev_manager = get_event_manager()
        keys = pg.key.get_pressed()
        direction = pg.Vector2(0, 0)
        for k, v in const.PLAYER_KEYS.items():
            if keys[k]:
                direction += v
        if direction.length() != 0:
            ev_manager.post(EventPlayerMove(direction))
