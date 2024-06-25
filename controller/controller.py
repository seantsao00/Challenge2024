"""
The module defines Controller class.
"""

import pygame as pg

import const
from event_manager import (EventEveryTick, EventHumanInput, EventInitialize,
                           EventQuit)
from instances_manager import get_event_manager, get_model
from model.timer import TimerManager


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
        """Do actions that should be executed every tick."""
        key_down_events = []
        ev_manager = get_event_manager()
        model = get_model()
        # Called once per game tick. We check our keyboard presses here.
        for event_pg in pg.event.get():
            # Handle window manager closing our window
            if event_pg.type == pg.QUIT:
                ev_manager.post(EventQuit())

            if event_pg.type == pg.KEYDOWN:
                # For orientating
                key_down_events.append(event_pg)

            if event_pg.type == pg.MOUSEBUTTONDOWN:
                mouse_pos = event_pg.pos
                x, y = mouse_pos
                w, h = pg.display.get_surface().get_size()
                w_canva_to_screen_ratio = w / const.WINDOW_SIZE[0]
                h_canva_to_screen_ratio = h / const.WINDOW_SIZE[1]
                x = x / w_canva_to_screen_ratio
                y = y / h_canva_to_screen_ratio
                if event_pg.button == 1:  # Left mouse button
                    print(f"Mouse click position: ({x}, {y})")
                    clicked = None
                    for entity in model.entities:
                        if (pg.Vector2(x, y) - entity.position).length() < const.ENTITY_RADIUS:
                            clicked = entity
                    
                    ev_manager.post(EventHumanInput(const.INPUT_TYPES.PICK, clicked=clicked))

                if event_pg.button == 3:  # Right mouse button
                    print(f"Right click position: ({x}, {y})")
                    clicked = None
                    for entity in model.entities:
                        if (pg.Vector2(x, y) - entity.position).length() < const.ENTITY_RADIUS:
                            clicked = entity

                    ev_manager.post(EventHumanInput(const.INPUT_TYPES.ATTACK, clicked=clicked))

            TimerManager.handle_event(event_pg)

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
        and post EventHumanInput according to the keys pressed.
        """
        ev_manager = get_event_manager()
        pressed_keys = pg.key.get_pressed()

        direction = pg.Vector2(0, 0)

        for k, v in const.HUMAN_KEYS_MAP.items():
            # If the key is actually pressed
            if pressed_keys[k]:
                direction += v

        if direction.length() != 0:
            # Try to move as far as player can.
            displacement = direction.normalize() * max(const.PlayerSpeeds)
            ev_manager.post(EventHumanInput(const.INPUT_TYPES.MOVE, displacement=displacement))
