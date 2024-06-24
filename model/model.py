"""
The module defines the main game engine.
"""
import os

import pygame as pg

import const
import const.map
from event_manager import (EventCreateEntity, EventEveryTick, EventInitialize, EventPlayerMove,
                           EventQuit, EventMultiAttack)
from instances_manager import get_event_manager
from model.player import Player
from model.entity import Entity
from model.timer import Timer
from model.character import Character
from model.ranged_fighter import RangedFighter
from model.fountain import Fountain
from model.team import Team
from model.map import load_map

class Model:
    """
    The main game engine.

    The main loop of the game is in Model.run()
    """

    def __init__(self, map_name):
        """
        Initialize the Model object.

        This function is called when the model is created.
        For more specific objects related to a game instance,
        (e.g., The time that has elapsed in the game, )
        they should be initialized in Model.initialize()
        """
        self.running: bool = False
        self.state = const.State.PAUSE
        self.clock = pg.time.Clock()
        self.players: dict[const.PlayerIds, Player] = {}
        self.entities: list[Entity] = []
        self.register_listeners()
        self.dt = 0
        self.map = load_map(os.path.join(const.map.MAP_DIR, map_name))

    def initialize(self, _: EventInitialize):
        """
        Initialize attributes related to a game.

        This method should be called when a new game is about to start,
        even for the second or more rounds of the game.
        """
        self.players = {player_id: Player(player_id) for player_id in const.PlayerIds}
        self.state = const.State.PLAY
        team1 = Team("team1")
        self.test_fountain = Fountain((const.ARENA_SIZE[0] / 2, const.ARENA_SIZE[1] / 2), team1)
        team1.set_fountain(self.test_fountain)
        
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
        player.move(event.displacement, self.dt)

    def register_entity(self, event: EventCreateEntity):
        self.entities.append(event.entity)

    def multi_attack(self, event: EventMultiAttack):
        attacker = event.attacker
        type = event.type
        if (type == 1):
            origin: pg.Vector2 = event.target
            radius = event.radius
            for victim in self.entities:
                dist = origin.distance_to(victim.postition)
                if (attacker.team != victim.team and dist <= radius):
                    victim.take_damage(attacker.damage)

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
        while self.running:
            ev_manager.post(EventEveryTick())
            self.dt = self.clock.tick(const.FPS) / 1000.0
