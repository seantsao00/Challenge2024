"""
The module defines the main game engine.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pygame as pg

import const
import const.map
from api.internal import call_ai, load_ai
from event_manager import (EventCharacterDied, EventCharacterMove, EventCreateEntity,
                           EventEveryTick, EventInitialize, EventPauseModel, EventQuit,
                           EventRestartGame, EventResumeModel, EventSpawnCharacter, EventStartGame,
                           EventUnconditionalTick)
from instances_manager import get_event_manager
from model.building import Tower
from model.character import Character
from model.clock import Clock
from model.grid import Grid
from model.map import load_map
from model.pause_menu import PauseMenu
from model.team import Team

if TYPE_CHECKING:
    from model.entity import Entity
    from model.map import Map


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
        self.__running: bool = False
        self.state: const.State = const.State.COVER

        self.global_clock: pg.Clock = pg.time.Clock()
        """The clock since program start."""
        self.__game_clock: Clock = Clock()
        """The clock since game start, and will be paused when the game pause."""

        self.entities: list[Entity] = []
        self.map: Map = load_map(os.path.join(const.MAP_DIR, map_name))
        self.grid: Grid = Grid(900, 900)
        self.teams: list[Team]
        self.__tower: list[Tower] = []

        self.__team_files_names: list[str] = team_files
        self.show_view_range: bool = show_view_range
        self.show_attack_range: bool = show_attack_range

        self.pause_menu: PauseMenu = PauseMenu()

        self.__register_listeners()

    def __initialize(self, _: EventInitialize):
        """
        Initialize attributes related to a game.

        This method should be called when a new game is about to start,
        even for the second or more rounds of the game.
        """
        load_ai(self.__team_files_names)

        self.teams = []

        for i, team_master in enumerate(self.__team_files_names):
            new_position = pg.Vector2(self.map.fountains[i])
            team = Team(new_position, team_master == 'human')
            self.teams.append(team)
            self.__tower.append(Tower(new_position, team, 1))
        for team in self.teams:
            for i in range(len(self.teams)):
                if i != team.id:
                    get_event_manager().register_listener(EventSpawnCharacter,
                                                          team.handle_others_character_spawn, i)
        for position in self.map.neutral_towers:
            self.__tower.append(Tower(position))
        self.state = const.State.PLAY

    def __handle_every_tick(self, _: EventEveryTick):
        """
        Do actions that should be executed every tick.

        This method is called every tick.
        For example, if players will get point every tick, it might be done here. 
        """
        for i in range(len(self.teams)):
            call_ai(i)

    def __handle_quit(self, _: EventQuit):
        """
        Exit the main loop.
        """
        self.__running = False

    def __handle_pause(self, _: EventPauseModel):
        """
        Pause the game
        """
        self.state = const.State.PAUSE
        self.pause_menu.enable_menu()

    def __handle_resume(self, _: EventResumeModel):
        """
        Resume the game
        """
        self.state = const.State.PLAY
        self.pause_menu.disable_menu()

    def __handle_start(self, _: EventStartGame):
        """
        Start the game and post EventInitialize
        """
        ev_manager = get_event_manager()
        ev_manager.post(EventInitialize())

    def __register_entity(self, event: EventCreateEntity):
        self.entities.append(event.entity)
        if isinstance(event.entity, Character):
            for tower in self.grid.get_attacker_tower(event.entity.position):
                tower.enemy_in_range(event.entity)

    def __handle_character_died(self, event: EventCharacterDied):
        print("died event")
        self.grid.delete_from_grid(event.character, event.character.position)
        for tower in self.grid.get_attacker_tower(event.character.position):
            tower.enemy_out_range(event.character)

    def __handle_character_move(self, event: EventCharacterMove):
        for tower in self.grid.get_attacker_tower(event.original_pos):
            tower.enemy_out_range(event.character)
        for tower in self.grid.get_attacker_tower(event.character.position):
            tower.enemy_in_range(event.character)
        event.character.team.update_visible_entities_list(event.character)

    def __restart_game(self, _: EventRestartGame):
        get_event_manager().post(EventInitialize())

    def __register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.__initialize)
        ev_manager.register_listener(EventEveryTick, self.__handle_every_tick)
        ev_manager.register_listener(EventQuit, self.__handle_quit)
        ev_manager.register_listener(EventPauseModel, self.__handle_pause)
        ev_manager.register_listener(EventResumeModel, self.__handle_resume)
        ev_manager.register_listener(EventStartGame, self.__handle_start)
        ev_manager.register_listener(EventCreateEntity, self.__register_entity)
        ev_manager.register_listener(EventCharacterMove, self.__handle_character_move)
        ev_manager.register_listener(EventCharacterDied, self.__handle_character_died)
        ev_manager.register_listener(EventRestartGame, self.__restart_game)

    def get_time(self):
        return self.__game_clock.get_time()

    def run(self):
        """Run the main loop of the game."""
        self.__running = True
        # Tell every one to start
        ev_manager = get_event_manager()

        while self.__running:
            ev_manager.post(EventUnconditionalTick())
            if self.state == const.State.PLAY:
                ev_manager.post(EventEveryTick())
                self.global_clock.tick(const.FPS)
