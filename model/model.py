"""
The module defines the main game engine.
"""

import pygame as pg

import const
from event_manager import EventEveryTick, EventInitialize, EventPlayerMove, EventQuit, EventCreateEntity, EventAttack
from instances_manager import get_event_manager
from model.player import Player
from model.entity import Entity
from model.character import Character


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
        self.players: dict[const.PlayerIds, Player] = {}
        self.entities: list[Entity] = []
        self.register_listeners()
        test_entity = Entity(pg.Vector2(400, 300))
    
        ev_manager = get_event_manager()
        test_character1 = Character(1, pg.Vector2(200, 200), 5, 100, 10, 100, 100)
        ev_manager.register_listener(EventAttack, test_character1.take_damage, test_character1.id)

        test_character2 = Character(2, pg.Vector2(201, 201), 5, 100, 10, 100, 100)
        ev_manager.register_listener(EventAttack, test_character2.take_damage, test_character2.id)
        # print(test_character2.health)
        test_character1.attack(test_character2)
        # print(test_character2.health)

    def initialize(self, _: EventInitialize):
        """
        Initialize attributes related to a game.

        This method should be called when a new game is about to start,
        even for the second or more rounds of the game.
        """
        self.players = {player_id: Player(player_id) for player_id in const.PlayerIds}
        self.state = const.State.PLAY

    def handle_every_tick(self, _: EventEveryTick):
        """
        Do actions that should be executed every tick.

        This method is called every tick.
        For example, if players will get point every tick, it might be done here. 
        """

    def handle_quit(self, _: EventQuit):
        """
        Exit the main loop.
        """
        self.running = False

    def handle_player_move(self, event: EventPlayerMove):
        """
        Call Player.move() for each EventPlayerMove.
        """
        player = self.players[event.player_id]
        player.move(event.displacement)

    def register_entity(self, event: EventCreateEntity):
        self.entities.append(event.entity)

    def register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        ev_manager.register_listener(EventQuit, self.handle_quit)
        ev_manager.register_listener(EventPlayerMove, self.handle_player_move)
        ev_manager.register_listener(EventCreateEntity, self.register_entity)

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
