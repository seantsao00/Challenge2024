"""
The module defines the main game engine.
"""
from __future__ import annotations

import os.path
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame as pg

import const
import const.map
import const.model
from api.internal import load_ai, start_ai
from event_manager import (EventAttack, EventBulletCreate, EventBulletDamage, EventBulletDisappear,
                           EventBulletExplode, EventCharacterDied, EventCharacterMove,
                           EventCreateEntity, EventEveryTick, EventGameOver, EventInitialize,
                           EventPauseModel, EventPostInitialize, EventQuit,
                           EventRangedBulletDamage, EventResumeModel, EventSelectParty,
                           EventSpawnCharacter, EventStartGame, EventUnconditionalTick)
from instances_manager import get_event_manager
from model.building import Tower
from model.character import Character, Ranger, Sniper
from model.clock import Clock
from model.grid import Grid
from model.map import load_map
from model.party_selector import PartySelector
from model.pause_menu import PauseMenu
from model.team import NeutralTeam, Team
from model.timer import Timer
from util import log_critical

if TYPE_CHECKING:
    from model.entity import Entity
    from model.map import Map


@dataclass(kw_only=True)
class ModelArguments:
    topography: str
    team_controls: list[str]
    show_view_range: bool
    show_attack_range: bool
    skip_character_selection: bool


class Model:
    """
    The main game engine.

    The main loop of the game is in Model.run()
    """

    # def __init__(self, map_name: str, team_files: list[str], show_view_range: bool, show_attack_range: bool):
    def __init__(self, model_arguments: ModelArguments):
        """
        Initialize the Model object.

        This function is called when the model is created.
        For more specific objects related to a game instance,
        (e.g., The time that has elapsed in the game, )
        they should be initialized in Model.initialize()
        """
        self.__running: bool = False
        self.state: const.State = const.State.COVER

        self.global_clock: pg.time.Clock = pg.time.Clock()
        """The clock since program start."""
        self.__game_clock: Clock
        """The clock since game start(since player hit START_BUTTON), and will be paused when the game is paused."""
        self.__ticks: int = 0
        self.dt: float
        """Real-world-passing time since last tick in second."""

        self.entity_lock = threading.Lock()
        self.entities: list[Entity] = []
        self.map: Map = load_map(os.path.join(const.MAP_DIR, model_arguments.topography))
        self.grid: Grid = Grid(250, 250)
        self.party_selector: PartySelector = PartySelector(len(model_arguments.team_controls))
        if model_arguments.skip_character_selection:
            self.party_selector.select_random_party()
        self.teams: list[Team] = []
        self.__neutral_team: NeutralTeam
        self.__tower: list[Tower] = []
        self.__team_thread: list[threading.Thread] = [None] * len(model_arguments.team_controls)
        self.__team_files_names: list[str] = model_arguments.team_controls
        self.show_view_range: bool = model_arguments.show_view_range
        self.show_attack_range: bool = model_arguments.show_attack_range

        self.pause_menu: PauseMenu = PauseMenu()
        self.ranger_ability = False
        self.ranger_controlling: Ranger = None

        self.__register_listeners()

    def __initialize(self, _: EventInitialize):
        """
        Initialize attributes related to a game.

        This method should be called when a new game is about to start,
        even for the second or more rounds of the game.
        """
        self.__game_clock = Clock()

        self.teams: list[Team] = []

        selected_parties = self.party_selector.selected_parties()

        for i, team_master in enumerate(self.__team_files_names):
            new_position = pg.Vector2(self.map.fountains[i])
            team = Team(team_master == 'human',
                        selected_parties[i],
                        team_master)
            fountain = Tower(new_position, team, True)
            self.teams.append(team)
            self.__tower.append(fountain)
            team.fountain = fountain
        for team in self.teams:
            for i in (team.team_id for team in self.teams):
                if i != team.team_id:
                    get_event_manager().register_listener(EventSpawnCharacter,
                                                          team.handle_others_character_spawn, i)

        self.__neutral_team = NeutralTeam(const.PartyType.NEUTRAL)
        for position in self.map.neutral_towers:
            self.__tower.append(Tower(position, self.__neutral_team))
        self.state = const.State.PLAY

    def __post_initialize(self, _: EventPostInitialize):
        load_ai(self.__team_files_names)

    def __handle_every_tick(self, _: EventEveryTick):
        """
        Do actions that should be executed every tick.

        This method is called every tick.
        For example, if players will get point every tick, it might be done here. 
        """
        self.__ticks += 1
        self.__ticks %= const.TICKS_PER_CYCLE
        if self.__ticks == 0:
            for i in range(len(self.teams)):
                if self.__team_thread[i] is None or not self.__team_thread[i].is_alive():
                    self.__team_thread[i] = start_ai(i)
                else:
                    log_critical(
                        f"[API] AI of team {i} occurs a hard-to-kill timeout. New thread is NOT started.")

    def __register_entity(self, event: EventCreateEntity):
        with self.entity_lock:
            self.entities.append(event.entity)
        if isinstance(event.entity, Character):
            for tower in self.grid.get_attacker_tower(event.entity.position):
                tower.enemy_in_range(event.entity)

    def __handle_character_died(self, event: EventCharacterDied):
        for tower in self.grid.get_attacker_tower(event.character.position):
            tower.enemy_out_range(event.character)

    def __handle_character_move(self, event: EventCharacterMove):
        for tower in self.grid.get_attacker_tower(event.original_pos):
            tower.enemy_out_range(event.character)
        for tower in self.grid.get_attacker_tower(event.character.position):
            tower.enemy_in_range(event.character)
        event.character.team.vision.handle_character_move(event)

    def create_bullet(self, event: EventBulletCreate):
        get_event_manager().register_listener(EventEveryTick, event.bullet.judge)

    def ranged_bullet_damage(self, event: EventRangedBulletDamage):
        get_event_manager().unregister_listener(EventEveryTick, event.bullet.judge)
        event.bullet.state = const.BulletState.EXPLODE
        with self.entity_lock:
            for entity in self.entities:
                if (entity.position - event.bullet.target).length() < event.bullet.range and entity.team is not event.bullet.team:
                    get_event_manager().post(EventAttack(victim=entity,
                                                         attacker=event.bullet.attacker,
                                                         damage=event.bullet.damage), channel_id=entity.id)
        Timer(const.BULLET_RANGER_ABILITY_DURATION, get_event_manager().post,
              EventBulletExplode(bullet=event.bullet), once=True)

    def bullet_damage(self, event: EventBulletDamage):
        get_event_manager().unregister_listener(EventEveryTick, event.bullet.judge)
        event.bullet.discard()
        damage = event.bullet.damage
        if isinstance(event.bullet.attacker, Sniper) and isinstance(event.bullet.victim, Tower):
            damage /= const.BULLET_SNIPER_ATTACK_TOWER_DEBUFF
        get_event_manager().post(EventAttack(victim=event.bullet.victim,
                                             attacker=event.bullet.attacker,
                                             damage=damage), channel_id=event.bullet.victim.id)

    def bullet_disappear(self, event: EventBulletDisappear):
        get_event_manager().unregister_listener(EventEveryTick, event.bullet.judge)
        event.bullet.discard()

    def bullet_explode(self, event: EventBulletExplode):
        event.bullet.discard()

    def __register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventInitialize, self.__initialize)
        ev_manager.register_listener(EventInitialize, self.__post_initialize)
        ev_manager.register_listener(EventEveryTick, self.__handle_every_tick)
        ev_manager.register_listener(EventQuit, self.__handle_quit)
        ev_manager.register_listener(EventPauseModel, self.__handle_pause)
        ev_manager.register_listener(EventResumeModel, self.__handle_resume)
        ev_manager.register_listener(EventStartGame, self.__handle_start)
        ev_manager.register_listener(EventCreateEntity, self.__register_entity)
        ev_manager.register_listener(EventCharacterMove, self.__handle_character_move)
        ev_manager.register_listener(EventCharacterDied, self.__handle_character_died)
        ev_manager.register_listener(EventGameOver, self.handle_game_over)
        ev_manager.register_listener(EventBulletCreate, self.create_bullet)
        ev_manager.register_listener(EventRangedBulletDamage, self.ranged_bullet_damage)
        ev_manager.register_listener(EventBulletDamage, self.bullet_damage)
        ev_manager.register_listener(EventBulletDisappear, self.bullet_disappear)
        ev_manager.register_listener(EventSelectParty, self.__handle_select_party)
        ev_manager.register_listener(EventBulletExplode, self.bullet_explode)

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
                running_time = self.get_time()
                if running_time >= const.model.GAME_TIME:
                    ev_manager.post(EventGameOver())
            self.dt = self.global_clock.tick(const.FPS) / 1000

    def __handle_quit(self, _: EventQuit):
        """
        Exit the main loop.
        """
        self.__running = False

    def __handle_pause(self, _: EventPauseModel):
        """
        Pause the game.
        """
        self.state = const.State.PAUSE
        self.pause_menu.enable_menu()

    def __handle_resume(self, _: EventResumeModel):
        """
        Resume the game.
        """
        self.state = const.State.PLAY
        self.pause_menu.disable_menu()

    def __handle_start(self, _: EventStartGame):
        """
        Start the game and post EventInitialize.
        """
        ev_manager = get_event_manager()
        ev_manager.post(EventInitialize())
        ev_manager.post(EventPostInitialize())

    def handle_game_over(self, _: EventGameOver):
        """
        End the game and show scoreboard on the settlement screen.
        """
        self.state = const.State.SETTLEMENT

    def __handle_select_party(self, _: EventSelectParty):
        self.state = const.State.SELECT_PARTY
