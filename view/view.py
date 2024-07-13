"""
The module defines View class.
"""

import os

import cv2
import pygame as pg

import const
import const.model
import const.visual
from const.visual.priority import PRIORITY_BACKGROUND, PRIORITY_FOREGROUND, PRIORITY_VISION_MASK
from event_manager import (EventCreateEntity, EventInitialize, EventUnconditionalTick,
                           EventViewChangeTeam)
from instances_manager import get_event_manager, get_model
from util import load_image
from view.object import (AbilitiesCDView, AttackRangeView, BackgroundObject, ChatView, ClockView,
                         EntityView, HealthView, ObjectBase, Particle, ParticleManager,
                         PartySelectorView, PauseMenuView, ScoreboardView, TowerCDView,
                         ViewRangeView, TrajectoryView)
from view.screen_info import ScreenInfo
from view.textutil import font_loader


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

        display_info = pg.display.Info()
        screen_w = int(min(display_info.current_w, display_info.current_h /
                       const.WINDOW_SIZE[1] * const.WINDOW_SIZE[0]) * const.SCREEN_FIT_RATIO)
        screen_h = int(min(display_info.current_h, display_info.current_w /
                       const.WINDOW_SIZE[0] * const.WINDOW_SIZE[1]) * const.SCREEN_FIT_RATIO)
        self.__screen: pg.Surface = pg.display.set_mode(size=(screen_w, screen_h))

        ScreenInfo.set_screen_info(screen_w / const.WINDOW_SIZE[0], (screen_w, screen_h))

        pg.display.set_icon(pg.image.load(const.ICON_IMAGE))

        self.__arena: pg.Surface = pg.Surface(size=(screen_h, screen_h))

        self.__pause_menu_view = PauseMenuView(self.__screen, model.pause_menu)
        self.__party_selector_view = PartySelectorView(self.__screen, model.party_selector)

        self.__cover_image: pg.Surface = load_image(const.COVER_IMAGE, screen_w, screen_h)[0]
        self.__particle_manager = ParticleManager(self.__arena)

        PartySelectorView.init_convert()

        self.__entities: list[EntityView] = []

        self.vision_of = 0
        self.scoreboard_image = pg.image.load(os.path.join(
            const.IMAGE_DIR, 'scoreboard.png')).convert_alpha()
        self.__background_images = []

        self.__scoreboxes = ScoreboardView(self.__screen)
        self.__chat = ChatView(self.__screen)
        self.__clock = ClockView(self.__screen)
        bg_image_counter = 0
        for filename in model.map.backgrounds:
            picture, position = load_image(os.path.join(
                model.map.map_dir, filename), screen_h, screen_h)
            self.__background_images.append(BackgroundObject(
                self.__arena, [PRIORITY_BACKGROUND, bg_image_counter], position, picture))
            bg_image_counter += 1
        for filename in model.map.objects:
            picture, position = load_image(os.path.join(
                model.map.map_dir, filename), screen_h, screen_h)
            self.__background_images.append(BackgroundObject(
                self.__arena, [PRIORITY_FOREGROUND, model.map.objects[filename]], position, picture))

        EntityView.init_convert()

        self.register_listeners()

    def initialize(self, _: EventInitialize):
        """
        Initialize components that require initialization at the start of every game.
        """

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
            if entity.alive:
                self.__entities.append(TrajectoryView(self.__arena, entity))
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
        elif model.state is const.State.SELECT_PARTY:
            self.render_party_selector()
        elif model.state is const.State.SETTLEMENT:
            self.render_settlement()
        pg.display.flip()

    def render_cover(self):
        """Render game cover"""
        self.__screen.blit(self.__cover_image, (0, 0))

    def render_party_selector(self):
        """Render party selecting process"""
        self.__party_selector_view.draw()

    def render_settlement(self):
        """Render the game settlement screen"""
        # setting up a temporary screen till we have a scoreboard image and settlement screen
        font = font_loader.get_font(size=12)
        text_surface = font.render('THIS IS SETTLEMENT SCREEN', True, pg.Color('white'))
        self.__screen.blit(text_surface, (100, 100))

    def render_play(self):
        """Render scenes when the game is being played"""
        model = get_model()

        self.scoreboard_image = pg.transform.scale(self.scoreboard_image, ScreenInfo.screen_size)
        self.__screen.blit(self.scoreboard_image, (0, 0))

        discarded_entities: set[type[EntityView]] = set()

        for entity in self.__entities:
            if not entity.move():
                discarded_entities.add(entity)
        self.__entities = [
            entity for entity in self.__entities if entity not in discarded_entities]

        for entity in discarded_entities:
            entity.unregister_listeners()

        objects: list[type[ObjectBase]] = []

        objects += self.__background_images

        if self.vision_of == 0:
            for entity in self.__entities:
                objects.append(entity)
        else:
            my_team = model.teams[self.vision_of - 1]
            mask = pg.transform.scale(my_team.vision.get_mask(),
                                      (ScreenInfo.screen_size[1], ScreenInfo.screen_size[1]))
            objects.append(BackgroundObject(self.__arena, [PRIORITY_VISION_MASK], (0, 0), mask))
            for obj in self.__entities:
                if my_team.vision.entity_inside_vision(obj.entity) is True:
                    objects.append(obj)

        objects.sort(key=lambda x: x.priority)
        for obj in objects:
            obj.draw()

        self.__screen.blit(
            self.__arena, ((ScreenInfo.screen_size[0] - ScreenInfo.screen_size[1]) / 2, 0))

        self.__scoreboxes.update()
        self.__scoreboxes.draw()
        self.__chat.update()
        self.__chat.draw()
        self.__clock.draw()

        self.__particle_manager.draw()

        if model.state == const.State.PAUSE:
            self.__pause_menu_view.draw()

    def change_vision_of(self, _: EventViewChangeTeam):
        self.vision_of = (self.vision_of + 1) % (len(get_model().teams) + 1)

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventUnconditionalTick, self.handle_unconditional_tick)
        ev_manager.register_listener(EventCreateEntity, self.handle_create_entity)
        ev_manager.register_listener(EventViewChangeTeam, self.change_vision_of)

    def display_fps(self):
        """Display the current fps on the window caption."""
        model = get_model()
        pg.display.set_caption(
            f'{const.WINDOW_CAPTION} - FPS: {model.global_clock.get_fps():.2f}')
