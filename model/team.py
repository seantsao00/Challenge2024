from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

import pygame as pg

import const
import const.team
from event_manager import (EventCharacterDied, EventCreateTower, EventEveryTick, EventHumanInput,
                           EventSelectCharacter, EventSpawnCharacter, EventTeamGainTower,
                           EventTeamLoseTower)
from instances_manager import get_event_manager, get_model
from model.building import Tower
from model.character import Character, Ranger

if TYPE_CHECKING:
    from model.entity import Entity, LivingEntity


class Team:

    """
    Class for Team in the game.
    Each Team has the following property:
     - name: The name of the team.
     - master: The controller of the team.
     - total_buildings: The total buildings that this team has.
     - points: The accumulated points of the team.
     - id: The id of the team.
     - building_list: list of the building of the team. The first one is the fountain.
     - character_list: list of the character of the team.
     - visible_entities_list: list of visible entities to the team. Note that entities owned by this team is not in this list.
    """

    __total: int = 0

    def __init__(self, manual_control: bool, party: const.PartyType, team_name: str | None = None):
        if Team.__total == 4:
            raise Exception('Team size exceeds.')
        self.__id = Team.__total
        Team.__total += 1

        self.__manual_control: bool = manual_control
        self.__party: const.PartyType = party
        if team_name:
            self.__team_name = team_name
        else:
            self.__team_name = "team" + str(Team.__total)
        self.__points: int = 0
        self.__towers: set[Tower] = set()
        self.__character_list: list[Character] = []
        self.__visible_entities_list: set[Entity] = set()
        self.__choosing_position: bool = False
        """For abilities that have to click mouse to cast."""
        self.__controlling: Entity | None = None
        self.register_listeners()

    def handle_input(self, event: EventHumanInput):
        """
        Handles input by human. This method is only used by human controlled teams.
        """
        clicked_entity = event.clicked_entity

        if event.input_type == const.InputTypes.PICK:
            if clicked_entity.team is self:
                self.__controlling = clicked_entity
            else:
                print('picked a non interactable entity')

        if self.__controlling is None:
            return

        if event.input_type == const.InputTypes.MOVE and isinstance(self.__controlling, Character):
            self.__controlling.move(event.displacement)
        elif event.input_type == const.InputTypes.ATTACK:
            if isinstance(self.__controlling, Character):
                if self.__choosing_position is True:
                    self.__controlling.cast_ability(event.displacement)
                    self.__choosing_position = False
                elif isinstance(clicked_entity, Tower) or isinstance(clicked_entity, Character):
                    self.__controlling.attack(clicked_entity)
        elif event.input_type is const.InputTypes.ABILITY:
            if isinstance(self.__controlling, Character):
                if isinstance(self.__controlling, Ranger):
                    self.__choosing_position = True
                else:
                    self.__controlling.cast_ability()

    def gain_character(self, event: EventSpawnCharacter):
        self.__character_list.append(event.character)

    def gain_tower(self, event: EventTeamGainTower):
        if event.tower not in self.__towers:
            self.__towers.add(event.tower)
        print(f'{self.__team_name} gained a tower with id {event.tower.__id} at {event.tower.__position}')

    def lose_tower(self, event: EventTeamLoseTower):
        print(f'{self.__team_name} lost a tower with id {event.tower.__id} at {event.tower.__position}')
        if event.tower in self.__towers:
            self.__towers.remove(event.tower)

    def gain_point_kill(self):
        self.__points += const.SCORE_KILL

    def gain_point_tower(self, _: EventEveryTick):
        self.__points += const.SCORE_OWN_TOWER * len(self.__towers)

    def handle_character_died(self, event: EventCharacterDied):
        if self.__controlling is event.character:
            self.__controlling = None
        if event.character in self.__character_list:
            self.__character_list.remove(event.character)
        if event.character in self.__visible_entities_list:
            self.__visible_entities_list.remove(event.character)

    def handle_create_tower(self, event: EventCreateTower):
        self.update_visible_entities_list(event.tower)

    def handle_others_character_spawn(self, event: EventSpawnCharacter):
        self.update_visible_entities_list(event.character)

    def update_visible_entities_list(self, entity: LivingEntity):
        """
        This function updates the current entities visible to the instance of Team.
        """
        if not entity.alive:
            return

        model = get_model()

        if entity.team is self:
            for other_entity in model.entities:
                if (other_entity.team is not self and
                        other_entity.position.distance_to(entity.position) <= entity.vision):
                    self.__visible_entities_list.add(other_entity)
        else:
            for my_entity in chain(self.__towers, self.__character_list):
                if my_entity.alive and entity.position.distance_to(my_entity.position) <= my_entity.vision:
                    self.__visible_entities_list.add(entity)
                    break

    def select_character(self, event: EventSelectCharacter):
        if isinstance(self.__controlling, Tower):
            self.__controlling.update_character_type(event.character)

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        if self.__manual_control:
            ev_manager.register_listener(EventHumanInput, self.handle_input)
        ev_manager.register_listener(EventCreateTower, self.handle_create_tower)
        ev_manager.register_listener(EventTeamGainTower, self.gain_tower, self.__id)
        ev_manager.register_listener(EventTeamLoseTower, self.lose_tower, self.__id)
        ev_manager.register_listener(EventSpawnCharacter, self.gain_character, self.__id)
        ev_manager.register_listener(EventSelectCharacter, self.select_character)
        ev_manager.register_listener(EventCharacterDied, self.handle_character_died)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def team_name(self) -> str:
        return self.__team_name

    @property
    def points(self) -> int:
        return self.__points

    @property
    def towers(self) -> const.PartyType:
        return self.__towers

    @property
    def party(self) -> const.PartyType:
        return self.__party
