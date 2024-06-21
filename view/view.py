"""
The module defines View class.
"""

import pygame as pg

import const
from event_manager import EventEveryTick, EventInitialize, EventPlayerMove, EventQuit
from instances_manager import get_event_manager, get_model
from view.object import ObjectBase, Player, Entity


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
        self.players: list[Player]
        self.entity: list[Entity]
        self.screen = pg.display.set_mode(size=const.WINDOW_SIZE)
        pg.display.set_caption(const.WINDOW_CAPTION)
        Player.init_convert()
        Entity.init_convert()
        self.register_listeners()

    def initialize(self, _: EventInitialize):
        """
        Initialize components that require initialization at the start of every game.
        """
        model = get_model()
        self.players = [Player(player) for _, player in model.players.items()]
        self.entity = [Entity(player) for _, player in model.players.items()]

    def handle_every_tick(self, _: EventEveryTick):
        self.display_fps()
        self.screen.fill(const.BACKGROUND_COLOR)
        objects: list[ObjectBase] = []
        objects += self.players
        model = get_model()
        for en in model.entities:
            objects.append(Entity(en))
            
        for obj in objects:
            # print(obj.images[obj.player.id][const.PlayerSpeeds.WALK].get_width())
            obj.draw(self.screen)
        
        # For test
        pg.draw.line(
            self.screen, 'white', (const.ARENA_SIZE[0], 0), (const.ARENA_SIZE[0], const.ARENA_SIZE[1] - 1), 1
        )
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
