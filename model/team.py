from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import TYPE_CHECKING

import const
import const.character
import const.team
from event_manager import (EventCharacterDied, EventCreateTower, EventEveryTick, EventHumanInput,
                           EventSelectCharacter, EventSpawnCharacter, EventTeamGainTower,
                           EventTeamLoseTower)
from instances_manager import get_event_manager, get_model
from model.building import Tower
from model.character import Character
from model.team_vision import TeamVision
from util import log_critical, log_info

if TYPE_CHECKING:
    from model.entity import Entity


class NeutralTeam:

    """
    super class of class Team.
    """

    _total: int = 0

    def __init__(self, party: const.PartyType):
        self.__team_id = NeutralTeam._total
        self.__party = party
        NeutralTeam._total += 1

    @property
    def team_id(self) -> int:
        return self.__team_id

    @property
    def party(self) -> const.PartyType:
        return self.__party


class Team(NeutralTeam):

    """
    Class for Team in the game.
    Each Team has the following property:
     - name: The name of the team.
     - master: The controller of the team.
     - total_buildings: The total buildings that this team has.
     - points: The accumulated points of the team.
     - id: The id of the team.
     - building_list: list of the building of the team.
     - fountain: fountain.
     - character_list: list of the character of the team.
     - visible_entities_list: list of visible entities to the team. Note that entities owned by this team is not in this list.
    """

    @dataclass
    class TeamStats:
        score: int
        units_alive: int
        units_dead: int
        units_killed: int

    def __init__(self, manual_control: bool, party: const.PartyType, team_name: str | None = None):
        super().__init__(party)

        self.__manual_control: bool = manual_control
        if team_name:
            self.__team_name = team_name
        else:
            self.__team_name = 'team' + str(self.__team_id + 1)
        self.__stats = Team.TeamStats(0, 0, 0, 0)
        self.__towers: set[Tower] = set()
        self.tower_lock = Lock()
        self.character_lock = Lock()
        self.character_list: set[Character] = set()
        self.fountain: Tower = None
        """For abilities that have to click mouse to cast."""
        self.__controlling: Entity | None = None
        self.vision = TeamVision(self)
        self.register_listeners()

    def handle_input(self, event: EventHumanInput):
        """
        Handles input by human. This method is only used by human controlled teams.
        """

        clicked_entity = event.clicked_entity

        if event.input_type == const.InputTypes.PICK:
            if clicked_entity is None:
                log_critical('post EventHumanInput PICK without clicked entity')
                return
            if clicked_entity.team is self:
                if isinstance(self.__controlling, Character) and self.__controlling.team is self:
                    self.__controlling.set_move_stop()
                self.__controlling = clicked_entity
            else:
                log_info('selected an entity that is not for your team')

        if self.__controlling is None:
            return

        if event.input_type == const.InputTypes.MOVE and isinstance(self.__controlling, Character):
            self.__controlling.set_move_direction(event.displacement)
        elif event.input_type == const.InputTypes.ATTACK:
            if isinstance(self.__controlling, Character):
                self.__controlling.attack(clicked_entity)
            else:
                log_info(
                    f'try to attack when controlling {self.__controlling}, which can not attack')
        elif event.input_type is const.InputTypes.ABILITY:
            if isinstance(self.__controlling, Character):
                self.__controlling.manual_cast_ability()

    def gain_character(self, event: EventSpawnCharacter):
        with self.character_lock:
            self.character_list.add(event.character)
        self.__stats.units_alive += 1

    def gain_tower(self, event: EventTeamGainTower):
        with self.tower_lock:
            if event.tower not in self.__towers:
                self.__towers.add(event.tower)
                self.vision.update_vision(event.tower)
        log_info(f'{self.__team_name} gained a tower '
                 f'with id {event.tower.id} at {event.tower.position}')
        model = get_model()
        if model.state is const.State.PLAY:
            model.chat.send_system(f'{self.__team_name} gained a tower')

    def lose_tower(self, event: EventTeamLoseTower):
        log_info(f'{self.__team_name} lost a tower '
                 f'with id {event.tower.id} at {event.tower.position}')
        model = get_model()
        if model.state is const.State.PLAY or model.state is const.State.PAUSE:
            model.chat.send_system(f'{self.__team_name} lost a tower')
        with self.tower_lock:
            if event.tower in self.__towers:
                self.__towers.remove(event.tower)

    def gain_point_kill(self):
        self.__stats.score += const.SCORE_KILL
        self.__stats.units_killed += 1

    def gain_point_tower(self, _: EventEveryTick):
        self.__stats.score += const.SCORE_OWN_TOWER * len(self.__towers) * get_model().dt

    def handle_character_died(self, event: EventCharacterDied):
        if self.__controlling is event.character:
            self.__controlling = None
        with self.character_lock:
            if event.character in self.character_list:
                self.character_list.remove(event.character)
                self.__stats.units_alive -= 1
                self.__stats.units_dead += 1

    def handle_create_tower(self, event: EventCreateTower):
        if event.tower.team is self:
            self.vision.update_vision(event.tower)

    def handle_others_character_spawn(self, event: EventSpawnCharacter):
        if event.character.team is self:
            self.vision.update_vision(event.character)

    def select_character(self, event: EventSelectCharacter):
        if isinstance(self.__controlling, Tower) and self.__controlling.team == self:
            log_info(
                f'Character type of team {self.team_id + 1} is modified to {event.character_type}')
            self.__controlling.update_character_type(event.character_type)

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        if self.__manual_control:
            ev_manager.register_listener(EventHumanInput, self.handle_input)
        ev_manager.register_listener(EventCreateTower, self.handle_create_tower)
        ev_manager.register_listener(EventTeamGainTower, self.gain_tower, self.team_id)
        ev_manager.register_listener(EventTeamLoseTower, self.lose_tower, self.team_id)
        ev_manager.register_listener(EventSpawnCharacter, self.gain_character, self.team_id)
        ev_manager.register_listener(EventSelectCharacter, self.select_character)
        ev_manager.register_listener(EventCharacterDied, self.handle_character_died)
        ev_manager.register_listener(EventEveryTick, self.gain_point_tower)

    @property
    def team_name(self) -> str:
        return self.__team_name

    @property
    def points(self) -> int:
        return self.__stats.score

    @property
    def stats(self) -> Team.TeamStats:
        return self.__stats

    @property
    def towers(self) -> const.PartyType:
        return self.__towers

    # @property
    # def visible_entities_list(self):
    #     return self.__visible_entities_list
