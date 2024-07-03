"""
The module defines the main game engine.
"""
import os
from random import randint

import pygame as pg

import const
from event_manager import (EventCreateEntity, EventEveryTick, EventInitialize, EventMultiAttack,
                           EventPauseModel, EventQuit, EventResumeModel, EventSpawnCharacter,
                           EventUnconditionalTick, EventAttack, EventCharacterDied, EventCharacterMove)
from instances_manager import get_event_manager
from model.building import Tower
from model.character import Character
from model.entity import Entity, LivingEntity
from model.grid import Grid
from model.map import load_map
from model.pause_menu import PauseMenu
from model.team import Team


class Model:
    """
    The main game engine.

    The main loop of the game is in Model.run()
    """

    def __init__(self, map_name: str, teams: list[Team], show_view_range: bool, show_attack_range: bool):
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
        self.team_names = teams
        self.teams: list[Team] = None
        self.show_view_range = show_view_range
        self.show_attack_range = show_attack_range
        self.pause_menu = PauseMenu()
        self.characters = set()
        self.grid = Grid(900, 900)
        self.stop_time = 0
        self.tower_occupied: list[list[set[Tower]]] = [[set() for _ in range(900)] for _ in range(900)]
        self.tower: list[Tower] = []

    def initialize(self, _: EventInitialize):
        """
        Initialize attributes related to a game.

        This method should be called when a new game is about to start,
        even for the second or more rounds of the game.
        """
        self.state = const.State.PLAY
        self.teams = []

        for i, team_master in enumerate(self.team_names):
            new_position = pg.Vector2(
                randint(100, const.ARENA_SIZE[0] - 100), randint(100, const.ARENA_SIZE[1]) - 100)
            team = Team(new_position, "team" + str(i+1), team_master)
            self.teams.append(team)
            self.tower.append(Tower(new_position, team, 1))
        for team in self.teams:
            for i in range(len(self.teams)):
                if i + 1 != team.id:
                    get_event_manager().register_listener(EventSpawnCharacter,
                                                          team.handle_others_character_spawn, i + 1)
        
        self.tower.append(Tower((700, 700)))
        for i in self.tower:
            for x in range(max(0, int(i.position.x - i.attack_range)), min(900, int(i.position.x + i.attack_range))):
                for y in range(max(0, int(i.position.y - i.attack_range)), min(900, int(i.position.y + i.attack_range))):
                    in_range = 0
                    for dx, dy in [[0, 0], [0, 1], [1, 0], [1, 1]]:
                        if i.position.distance_to(pg.Vector2(x + dx, y + dy)) <= i.attack_range:
                            in_range = 1
                            break
                    if in_range:
                        self.tower_occupied[x][y].add(i)

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
            for tower in self.tower_occupied[x][y]:
                tower.enemy_in_range(event.entity)

    def multi_attack(self, event: EventMultiAttack):
        attacker = event.attacker
        origin: pg.Vector2 = event.target
        radius = event.radius
        for victim in self.entities:
            if isinstance(victim, Character):
                dist = origin.distance_to(victim.position)
                if (attacker.team != victim.team and dist <= radius):
                    get_event_manager().post(EventAttack(attacker=attacker, victim=victim), victim.id)

    def handle_character_died(self, event: EventCharacterDied):
        self.grid.delete_from_grid(event.character, event.character.position)
        self.teams[event.character.team.id - 1].handle_character_died(event.character)
        x, y = int(event.character.position.x), int(event.character.position.y)
        for tower in self.tower_occupied[x][y]:
            tower.enemy_out_range(event.character)
            print('died remove from', tower.position.x, tower.position.y)

    def handle_character_move(self, event: EventCharacterMove):
        x1, y1 = int(event.character.position.x), int(event.character.position.y)
        x2, y2 = int(event.original_pos.x), int(event.original_pos.y)
        union = set(self.tower_occupied[x1][y1] & self.tower_occupied[x2][y2])
        add = list(self.tower_occupied[x1][y1] - union)
        rem = list(self.tower_occupied[x2][y2] - union)
        for tower in rem:
            tower.enemy_out_range(event.character)
        for tower in add:
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
        ev_manager.register_listener(EventMultiAttack, self.multi_attack)
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
