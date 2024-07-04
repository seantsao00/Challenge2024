"""
The module defines the main game engine.
"""
from __future__ import annotations

import os
from random import randint
from typing import TYPE_CHECKING

import pygame as pg

import const
from api.internal import call_ai, load_ai
from event_manager import (EventAttack, EventCharacterDied, EventCharacterMove, EventCreateEntity,
                           EventEveryTick, EventInitialize, EventPauseModel, EventQuit, 
                           EventResumeModel, EventSpawnCharacter, EventUnconditionalTick)
from instances_manager import get_event_manager
from model.building import Tower
from model.character import Character
from model.grid import Grid
from model.map import load_map
from model.pause_menu import PauseMenu
from model.team import Team

if TYPE_CHECKING:
    from model.entity import Entity


class Model:
    """
    The main game engine.

    The main loop of the game is in Model.run()
    """

    def __init__(self, map_name: str, team_files: list[str], show_view_range: bool, show_attack_range: bool):
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
        self.entities: list[Entity] = []
        self.register_listeners()
        self.dt = 0
        self.map = load_map(os.path.join(const.MAP_DIR, map_name))
        self.team_files_names: list[str] = team_files
        self.teams: list[Team] = None
        self.show_view_range = show_view_range
        self.show_attack_range = show_attack_range
        self.pause_menu = PauseMenu()
        self.characters = set()
        self.grid = Grid(900, 900)
        self.stop_time = 0
        self.tower: list[Tower] = []

    def initialize(self, _: EventInitialize):
        """
        Initialize attributes related to a game.

        This method should be called when a new game is about to start,
        even for the second or more rounds of the game.
        """
        load_ai(self.team_files_names)

        self.state = const.State.PLAY
        self.teams = []

        for i, team_master in enumerate(self.team_files_names):
            new_position = pg.Vector2(self.map.fountains[i])
            team = Team(new_position, team_master == 'human')
            self.teams.append(team)
            self.tower.append(Tower(new_position, team, 1))
        for team in self.teams:
            for i in range(len(self.teams)):
                if i != team.id:
                    get_event_manager().register_listener(EventSpawnCharacter,
                                                          team.handle_others_character_spawn, i)

        self.tower.append(Tower((700, 700)))

    def handle_every_tick(self, _: EventEveryTick):
        """
        Do actions that should be executed every tick.

        This method is called every tick.
        For example, if players will get point every tick, it might be done here. 
        """
        for i in range(len(self.teams)):
            call_ai(i)

    def handle_quit(self, _: EventQuit):
        """
        Exit the main loop.
        """
        self.running = False

    def handle_pause(self, _: EventPauseModel):
        """
        Pause the game
        """
        self.tmp_timer = pg.time.Clock()
        self.state = const.State.PAUSE

    def handle_resume(self, _: EventResumeModel):
        """
        Resume the game
        """
        self.stop_time += self.tmp_timer.tick()
        self.state = const.State.PLAY

    def get_time(self):
        return (pg.time.get_ticks() - self.stop_time) / 1000

    def register_entity(self, event: EventCreateEntity):
        self.entities.append(event.entity)
        if isinstance(event.entity, Character):
            self.characters.add(event.entity)
            x, y = int(event.entity.position.x), int(event.entity.position.y)
            for tower in self.grid.get_attacker_tower(event.entity.position):
                tower.enemy_in_range(event.entity)

    def handle_character_died(self, event: EventCharacterDied):
        print("died event")
        self.grid.delete_from_grid(event.character, event.character.position)
        for tower in self.grid.get_attacker_tower(event.character.position):
            tower.enemy_out_range(event.character)

    def handle_character_move(self, event: EventCharacterMove):
        for tower in self.grid.get_attacker_tower(event.original_pos):
            tower.enemy_out_range(event.character)
        for tower in self.grid.get_attacker_tower(event.character.position):
            tower.enemy_in_range(event.character)
        event.character.team.update_visible_entities_list(event.character)

    def register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.initialize)
        ev_manager.register_listener(EventEveryTick, self.handle_every_tick)
        ev_manager.register_listener(EventQuit, self.handle_quit)
        ev_manager.register_listener(EventPauseModel, self.handle_pause)
        ev_manager.register_listener(EventResumeModel, self.handle_resume)
        ev_manager.register_listener(EventCreateEntity, self.register_entity)
        ev_manager.register_listener(EventCharacterMove, self.handle_character_move)
        ev_manager.register_listener(EventCharacterDied, self.handle_character_died)

    def run(self):
        """Run the main loop of the game."""
        self.running = True
        # Tell every one to start
        ev_manager = get_event_manager()
        ev_manager.post(EventInitialize())
        while self.running:
            ev_manager.post(EventUnconditionalTick())
            if self.state == const.State.PLAY:
                ev_manager.post(EventEveryTick())
                self.dt = self.clock.tick(const.FPS) / 1000.0
                # print(self.get_time())
