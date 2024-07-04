"""
The module defines View class.
"""

import os
import time
from itertools import chain, zip_longest

import cv2
import numpy as np
import pygame as pg

import const
from event_manager import EventInitialize, EventStartGame, EventUnconditionalTick
from instances_manager import get_event_manager, get_model
from view.object import (AttackRangeView, EntityView, HealthView, ObjectBase, PauseMenuView,
                         ViewRangeView)
from view.object.background_object import BackGroundObject


class View:
    """
    The class that presents the actual game content on the screen.
    """

    def __init__(self, vision_of):
        """
        Initialize the View instance upon its creation.

        For more specific objects related to a game instance, 
        they should be initialized in View.initialize().
        """
        model = get_model()

        size = pg.display.Info()
        window_w = min(size.current_w, size.current_h /
                       const.WINDOW_SIZE[1] * const.WINDOW_SIZE[0])
        window_h = min(size.current_h, size.current_w /
                       const.WINDOW_SIZE[0] * const.WINDOW_SIZE[1])
        self.screen: pg.Surface = pg.display.set_mode(
            size=(window_w, window_h), flags=pg.RESIZABLE | pg.DOUBLEBUF)
        self.screen_size: tuple[int, int] = (window_w, window_h)
        pg.display.set_caption(const.WINDOW_CAPTION)
        self.ratio: float = window_w / const.WINDOW_SIZE[0]
        self.entities = []

        self.pause_menu_view = PauseMenuView(self.screen, self.ratio, model.pause_menu)

        self.background_images = []
        for i in model.map.images:
            loaded_image = cv2.imread(
                os.path.join(model.map.map_dir, i), cv2.IMREAD_UNCHANGED
            )
            loaded_image = cv2.resize(
                loaded_image, const.ARENA_SIZE, interpolation=cv2.INTER_AREA
            )
            # if loaded_image.shape[2] == 3:
            #     alpha_channel = np.ones(
            #         (loaded_image.shape[0], loaded_image.shape[1]), dtype=loaded_image.dtype) * 255
            #     loaded_image = np.dstack((loaded_image, alpha_channel))
            x, y, w, h = cv2.boundingRect(loaded_image[..., 3])
            picture = pg.image.load(os.path.join(model.map.map_dir, i)).convert_alpha()
            picture = pg.transform.scale(picture, const.ARENA_SIZE)
            picture = picture.subsurface(pg.Rect(x, y, w, h))
            self.background_images.append(BackGroundObject(
                self.screen, int(model.map.images[i]), (x, y), picture))

        if vision_of == 'all':
            self.vision_of = const.VIEW_EVERYTHING
        else:
            try:
                self.vision_of = int(vision_of)
            except ValueError:
                for i, team_name in enumerate(model.team_names):
                    if vision_of == team_name:
                        self.vision_of = i+1
                        break

        self.register_listeners()

    def initialize(self, _: EventInitialize):
        """
        Initialize components that require initialization at the start of every game.
        """

    def handle_unconditional_tick(self, _: EventUnconditionalTick):
        self.display_fps()
        self.screen.fill(const.BACKGROUND_COLOR)
        model = get_model()
        if model.state == const.State.COVER:
            self.render_cover()
            time.sleep(0.01)
        elif model.state == const.State.PLAY:
            self.render_play()
        pg.display.flip()

    def render_cover(self):
        """Render game cover"""

        # setting up a temporary cover till we have a cover image
        font = pg.font.Font(None, int(12*self.ratio))
        text_surface = font.render(
            'THIS IS COVER. Press Space to Start the game', True, pg.Color('white'))
        self.screen.blit(text_surface, (100, 100))

    def render_play(self):
        """Render scenes when the game is being played"""
        model = get_model()

        for view_object in chain(*zip_longest(*[en.view for en in model.entities], fillvalue=None)):
            if view_object is not None:
                view_object.update()

        objects = []

        objects += self.background_images

        if self.vision_of == const.VIEW_EVERYTHING:
            for view_object in chain(*zip_longest(*[en.view for en in model.entities], fillvalue=None)):
                if view_object is not None:
                    objects.append(view_object)
        else:
            my_team = model.teams[self.vision_of - 1]
            for view_object in chain(*zip_longest(*[en.view for en in chain(my_team.building_list,
                                                                            my_team.character_list,
                                                                            my_team.visible_entities_list)], fillvalue=None)):
                if view_object is not None:
                    objects.append(view_object)

        objects.sort(key=lambda x: x.height)
        for obj in objects:
            obj.draw()

        if model.state == const.State.PAUSE:
            self.pause_menu_view.draw()

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventUnconditionalTick, self.handle_unconditional_tick)

    def display_fps(self):
        """Display the current fps on the window caption."""
        model = get_model()
        pg.display.set_caption(
            f'{const.WINDOW_CAPTION} - FPS: {model.clock.get_fps():.2f}')
