"""
The module defines View class.
"""

import os

import cv2
import numpy as np
import pygame as pg
from itertools import chain, zip_longest

import const
from event_manager import EventEveryTick, EventInitialize
from instances_manager import get_event_manager, get_model


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
        model = get_model()

        size = pg.display.Info()
        self.arena = pg.display.set_mode(
            size=const.ARENA_SIZE, flags=pg.RESIZABLE | pg.DOUBLEBUF).copy()
        self.canvas = pg.display.set_mode( 
            size=const.WINDOW_SIZE, flags=pg.RESIZABLE | pg.DOUBLEBUF).copy() # Draw team UI(anything outside of arena) on self.canvas
        window_w = min(size.current_w, size.current_h / 9 * 16)
        window_h = min(size.current_h, size.current_w / 16 * 9)
        self.screen = pg.display.set_mode(
            size=(window_w, window_h), flags=pg.RESIZABLE | pg.DOUBLEBUF)
        self.background_images = []
        # print(self.screen.get_rect().size)
        pg.display.set_caption(const.WINDOW_CAPTION)

        for i in model.map.images:
            loaded_image = cv2.imread(
                os.path.join(model.map.map_dir, i), cv2.IMREAD_UNCHANGED
            )
            loaded_image = cv2.resize(
                loaded_image, const.ARENA_SIZE, interpolation=cv2.INTER_AREA
            )
            if loaded_image.shape[2] == 3:
                alpha_channel = np.ones(
                    (loaded_image.shape[0], loaded_image.shape[1]), dtype=loaded_image.dtype) * 255
                loaded_image = np.dstack((loaded_image, alpha_channel))
            x, y, w, h = cv2.boundingRect(loaded_image[..., 3])
            picture = pg.image.load(os.path.join(model.map.map_dir, i)).convert_alpha()
            picture = pg.transform.scale(picture, const.ARENA_SIZE)
            picture = picture.subsurface(pg.Rect(x, y, w, h))
            self.background_images.append((int(model.map.images[i]), picture, (x, y)))

        self.register_listeners()

    def initialize(self, _: EventInitialize):
        """
        Initialize components that require initialization at the start of every game.
        """

    def handle_every_tick(self, _: EventEveryTick):
        self.display_fps()
        self.canvas.fill(const.BACKGROUND_COLOR)
        self.arena.fill(const.BACKGROUND_COLOR)
        model = get_model()

        for view_object in chain(*zip_longest(*[en.view for en in model.entities], fillvalue=None)):
            if view_object != None: view_object.draw(self.arena)

        # the arena is now in the middle
        pg.draw.line(
            self.arena, 'white', (0, 0), (0, const.ARENA_SIZE[1] - 1), 1
        )
        pg.draw.line(
            self.arena, 'white', (const.ARENA_SIZE[0] - 1, 0), (const.ARENA_SIZE[0] - 1, const.ARENA_SIZE[1] - 1), 1
        )
        self.canvas.blit(self.arena, ((const.WINDOW_SIZE[0] - const.ARENA_SIZE[0]) / 2, 0))
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
