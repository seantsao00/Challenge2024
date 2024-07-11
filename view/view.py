"""
The module defines View class.
"""

import os

import cv2
import pygame as pg

import const
import const.model
import const.visual
from const.visual.priority import PRIORITY_BACKGROUD, PRIORITY_FOREGROUND, PRIORITY_VISION_MASK
from event_manager import (EventCreateEntity, EventInitialize, EventUnconditionalTick,
                           EventViewChangeTeam)
from instances_manager import get_event_manager, get_model
from view.object import (AbilitiesCDView, AttackRangeView, BackgroundObject, EntityView,
                         HealthView, ObjectBase, PartySelectionView, PauseMenuView, TowerCDView,
                         ViewRangeView)


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

        screen_info = pg.display.Info()
        window_w = int(min(screen_info.current_w, screen_info.current_h /
                       const.WINDOW_SIZE[1] * const.WINDOW_SIZE[0]) * const.SCREEN_FIT_RATIO)
        window_h = int(min(screen_info.current_h, screen_info.current_w /
                       const.WINDOW_SIZE[0] * const.WINDOW_SIZE[1]) * const.SCREEN_FIT_RATIO)

        self.window_w = window_w
        self.window_h = window_h

        self.__screen: pg.Surface = pg.display.set_mode(
            size=(window_w, window_h), flags=pg.RESIZABLE | pg.DOUBLEBUF)
        self.screen_size: tuple[int, int] = (window_w, window_h)

        pg.display.set_icon(pg.image.load(const.ICON_IMAGE))
        pg.display.set_caption(const.WINDOW_CAPTION)

        self.__resize_ratio: float = window_w / const.WINDOW_SIZE[0]
        self.set_screen_info()
        # self.__arena: pg.Surface = pg.Surface(size=(window_h, window_h))
        self.__arena: pg.Surface = pg.Surface(size=(window_h, window_h))

        self.__pause_menu_view = PauseMenuView(self.__screen, model.pause_menu)
        self.__party_selecyion_view = PartySelectionView(self.__screen, model.party_selector)

        PartySelectionView.init_convert()

        self.__entities: list[EntityView] = []

        self.vision_of = 0
        self.scoreboard_image = pg.image.load(os.path.join(
            const.IMAGE_DIR, 'scoreboard.png')).convert_alpha()
        self.__background_images = []

        def load_image(filename: str):
            loaded_image = cv2.imread(
                os.path.join(model.map.map_dir, filename), cv2.IMREAD_UNCHANGED
            )
            loaded_image = cv2.resize(
                loaded_image, (window_h, window_h), interpolation=cv2.INTER_AREA
            )
            # if loaded_image.shape[2] == 3:
            #     alpha_channel = np.ones(
            #         (loaded_image.shape[0], loaded_image.shape[1]), dtype=loaded_image.dtype) * 255
            #     loaded_image = np.dstack((loaded_image, alpha_channel))
            x, y, w, h = cv2.boundingRect(loaded_image[..., 3])
            picture = pg.image.load(os.path.join(model.map.map_dir, filename)).convert_alpha()
            picture = pg.transform.scale(picture, (window_h, window_h))
            picture = picture.subsurface(pg.Rect(x, y, w, h))
            return x, y, picture

        bg_image_counter = 0
        for i in model.map.backgrounds:
            x, y, picture = load_image(i)
            self.__background_images.append(BackgroundObject(
                self.__arena, [PRIORITY_BACKGROUD, bg_image_counter], (x, y), picture))
            bg_image_counter += 1
        for i in model.map.objects:
            x, y, picture = load_image(i)
            self.__background_images.append(BackgroundObject(
                self.__arena, [PRIORITY_FOREGROUND, model.map.objects[i]], (x, y), picture))

        EntityView.init_convert()

        self.register_listeners()

    def set_screen_info(self):
        PauseMenuView.set_screen_info(self.__resize_ratio, *self.screen_size)
        EntityView.set_screen_info(self.__resize_ratio, *self.screen_size)
        ViewRangeView.set_screen_info(self.__resize_ratio, *self.screen_size)
        AttackRangeView.set_screen_info(self.__resize_ratio, *self.screen_size)
        AbilitiesCDView.set_screen_info(self.__resize_ratio, *self.screen_size)
        HealthView.set_screen_info(self.__resize_ratio, *self.screen_size)
        TowerCDView.set_screen_info(self.__resize_ratio, *self.screen_size)
        PartySelectionView.set_screen_info(self.__resize_ratio, *self.screen_size)

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
            self.render_party_selection()
        elif model.state is const.State.SETTLEMENT:
            self.render_settlement()
        pg.display.flip()

    def render_cover(self):
        """Render game cover"""

        # setting up a temporary cover till we have a cover image
        font = pg.font.Font(None, int(12*self.__resize_ratio))
        text_surface = font.render(
            'THIS IS COVER. Press Space to Start the game', True, pg.Color('white'))
        self.__screen.blit(text_surface, (100, 100))

    def render_party_selection(self):
        """Render party selection process"""
        self.__party_selecyion_view.draw()

    def render_settlement(self):
        """Render the game settlement screen"""
        # setting up a temporary screen till we have a scoreboard image and settlement screen
        font = pg.font.Font(const.REGULAR_FONT, int(12*self.__resize_ratio))
        text_surface = font.render('THIS IS SETTLEMENT SCREEN', True, pg.Color('white'))
        self.__screen.blit(text_surface, (100, 100))

    def render_play(self):
        """Render scenes when the game is being played"""
        model = get_model()

        self.scoreboard_image = pg.transform.scale(self.scoreboard_image, self.screen_size)
        self.__screen.blit(self.scoreboard_image, (0, 0))

        discarded_entities: set[type[EntityView]] = set()

        for entity in self.__entities:
            if not entity.update():
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
            mask = pg.transform.scale(my_team.vision.get_mask(), (self.window_h, self.window_h))
            objects.append(BackgroundObject(self.__arena, [PRIORITY_VISION_MASK], (0, 0), mask))
            for obj in self.__entities:
                if my_team.vision.entity_inside_vision(obj.entity) is True:
                    objects.append(obj)

        objects.sort(key=lambda x: x.priority)
        for obj in objects:
            obj.draw()

        self.__screen.blit(self.__arena, ((self.screen_size[0]-self.screen_size[1]) / 2, 0))

        # show time remaining
        time_remaining = int(const.GAME_TIME - model.get_time())
        (minute, sec) = divmod(time_remaining, 60)
        font = pg.font.Font(const.REGULAR_FONT, int(12*self.__resize_ratio))
        time_remaining_surface = font.render(f'{minute:02d}:{sec:02d}', True, pg.Color('white'))
        self.__screen.blit(time_remaining_surface, (100, 100))

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
