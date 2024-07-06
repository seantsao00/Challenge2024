"""
The module defines View class.
"""

import os
from itertools import chain

import cv2
import pygame as pg

import const
from event_manager import EventCreateEntity, EventInitialize, EventUnconditionalTick
from instances_manager import get_event_manager, get_model
from view.object import (AbilitiesCDView, AttackRangeView, BackGroundObject, EntityView,
                         HealthView, ObjectBase, PauseMenuView, TowerCDView, ViewRangeView)


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

        screen_info = pg.display.Info()
        window_w = int(min(screen_info.current_w, screen_info.current_h /
                       const.WINDOW_SIZE[1] * const.WINDOW_SIZE[0]))
        window_h = int(min(screen_info.current_h, screen_info.current_w /
                       const.WINDOW_SIZE[0] * const.WINDOW_SIZE[1]))
        self.__screen: pg.Surface = pg.display.set_mode(
            size=(window_w, window_h), flags=pg.RESIZABLE | pg.DOUBLEBUF)
        self.screen_size: tuple[int, int] = (window_w, window_h)
        pg.display.set_caption(const.WINDOW_CAPTION)

        self.__resize_ratio: float = window_w / const.WINDOW_SIZE[0]
        self.set_resize_ratio()
        # self.__arena: pg.Surface = pg.Surface(size=(window_h, window_h))
        self.__arena: pg.Surface = pg.Surface(size=(window_h, window_h))

        self.__pause_menu_view = PauseMenuView(self.__screen, model.pause_menu)

        self.__entities: list[EntityView] = []

        self.__background_images = []
        for i in model.map.images:
            loaded_image = cv2.imread(
                os.path.join(model.map.map_dir, i), cv2.IMREAD_UNCHANGED
            )
            loaded_image = cv2.resize(
                loaded_image, (window_h, window_h), interpolation=cv2.INTER_AREA
            )
            # if loaded_image.shape[2] == 3:
            #     alpha_channel = np.ones(
            #         (loaded_image.shape[0], loaded_image.shape[1]), dtype=loaded_image.dtype) * 255
            #     loaded_image = np.dstack((loaded_image, alpha_channel))
            x, y, w, h = cv2.boundingRect(loaded_image[..., 3])
            picture = pg.image.load(os.path.join(model.map.map_dir, i)).convert_alpha()
            picture = pg.transform.scale(picture, (window_h, window_h))
            picture = picture.subsurface(pg.Rect(x, y, w, h))
            self.__background_images.append(BackGroundObject(
                self.__arena, int(model.map.images[i]), (x, y), picture))

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
        self.__register_permanent_listeners()

    def set_resize_ratio(self):
        PauseMenuView.set_resize_ratio(self.__resize_ratio)
        EntityView.set_resize_ratio(self.__resize_ratio)
        ViewRangeView.set_resize_ratio(self.__resize_ratio)
        AttackRangeView.set_resize_ratio(self.__resize_ratio)
        AbilitiesCDView.set_resize_ratio(self.__resize_ratio)
        HealthView.set_resize_ratio(self.__resize_ratio)
        TowerCDView.set_resize_ratio(self.__resize_ratio)

    def initialize(self, _: EventInitialize):
        """
        Initialize components that require initialization at the start of every game.
        """
        self.__register_listeners()

    def handle_create_entity(self, event: EventCreateEntity):
        from model import Character, Tower
        model = get_model()
        entity = event.entity
        self.__entities.append(EntityView(self.__arena, entity))
        if isinstance(entity, Character):
            if model.show_view_range:
                self.__entities.append(ViewRangeView(self.__arena, entity))
            if model.show_attack_range:
                self.__entities.append(AttackRangeView(self.__arena, entity))
            self.__entities.append(AbilitiesCDView(self.__arena, entity))
            if entity.health is not None:
                self.__entities.append(HealthView(self.__arena, entity))
        if isinstance(entity, Tower):
            if model.show_view_range:
                self.__entities.append(ViewRangeView(self.__arena, entity))
            if model.show_attack_range:
                self.__entities.append(AttackRangeView(self.__arena, entity))
            self.__entities.append(TowerCDView(self.__arena, entity))
            if not entity.is_fountain:
                self.__entities.append(HealthView(self.__arena, entity))

    def handle_unconditional_tick(self, _: EventUnconditionalTick):
        self.display_fps()
        self.__screen.fill(const.BACKGROUND_COLOR)
        self.__arena.fill(const.BACKGROUND_COLOR)
        model = get_model()
        if model.state is const.State.COVER:
            self.render_cover()
        elif model.state is const.State.PLAY or model.state is const.State.PAUSE:
            self.render_play()
        pg.display.flip()

    def render_cover(self):
        """Render game cover"""

        # setting up a temporary cover till we have a cover image
        font = pg.font.Font(None, int(12*self.__resize_ratio))
        text_surface = font.render(
            'THIS IS COVER. Press Space to Start the game', True, pg.Color('white'))
        self.__screen.blit(text_surface, (100, 100))

    def render_play(self):
        """Render scenes when the game is being played"""
        model = get_model()

        discarded_entities: list[type[EntityView]] = []

        for entity in self.__entities:
            if not entity.update():
                discarded_entities.append(entity)
        self.__entities = [
            entity for entity in self.__entities if entity not in discarded_entities]

        objects: list[type[ObjectBase]] = []

        objects += self.__background_images

        if self.vision_of == const.VIEW_EVERYTHING:
            for entity in self.__entities:
                objects.append(entity)
        else:
            my_team = model.teams[self.vision_of - 1]
            for entity in self.__entities:
                if entity.entity in chain(my_team.building_list, my_team.character_list, my_team.visible_entities_list):
                    objects.append(entity)

        objects.sort(key=lambda x: x.priority)
        for obj in objects:
            obj.draw()

        self.__screen.blit(self.__arena, ((self.screen_size[0]-self.screen_size[1]) / 2, 0))

        if model.state == const.State.PAUSE:
            self.__pause_menu_view.draw()

    def __register_permanent_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_permanent_listener(EventInitialize, self.initialize)
        ev_manager.register_permanent_listener(
            EventUnconditionalTick, self.handle_unconditional_tick)
        ev_manager.register_permanent_listener(EventCreateEntity, self.handle_create_entity)

    def __register_listeners(self):
        """Register all listeners of this object with the event manager."""
        # ev_manager = get_event_manager()

    def display_fps(self):
        """Display the current fps on the window caption."""
        model = get_model()
        pg.display.set_caption(
            f'{const.WINDOW_CAPTION} - FPS: {model.global_clock.get_fps():.2f}')
