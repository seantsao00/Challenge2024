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
from model.character import RangerFighter

if TYPE_CHECKING:
    from model.building import Tower
    from model.character import Character
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

    total = 0

    def __init__(self, fountain_position: pg.Vector2, manual_control: bool):
        if Team.total == 4:
            raise Exception('Team size exceeds.')
        self.id = Team.total
        Team.total += 1
        self.name = "team" + str(Team.total)
        self.points = 0
        self.manual_control = manual_control
        self.building_list: list[Tower] = []
        self.character_list: list[Character] = []
        self.visible_entities_list: set[Entity] = set()
        self.choose_position = False
        self.controlling = None
        self.register_listeners()

    def handle_input(self, event: EventHumanInput):
        """
        Handles input by human. This method is only used by human controlled teams.
        """
        def check_movable(entity: Entity, my_team: Team):
            """
            This function checks if the clicked entity is actually movable by the human controlled team.
            """
            if entity is None:
                return False
            if hasattr(entity, 'team') and entity.team is my_team and hasattr(entity, 'move'):
                return True
            return False

        clicked_tower: Tower = None
        clicked_character: Character = None
        clicked = const.CharTypes.NONE

        if event.clicked is not None and event.clicked.type == 'tower':
            clicked_tower = event.clicked
            clicked = const.CharTypes.TOWER
        elif event.clicked is not None:
            clicked_character = event.clicked
            clicked = const.CharTypes.CHAR

        if event.input_type == const.InputTypes.PICK:
            if clicked == const.CharTypes.TOWER:
                if hasattr(clicked_tower, 'update_character_type') and clicked_tower.team is self:
                    self.controlling = clicked_tower
                else:
                    print('clicked on non interactable tower')
            elif clicked == const.CharTypes.CHAR:
                if check_movable(clicked_character, self):
                    self.controlling = clicked_character
                else:
                    print('clicked on non interactable entity')

        if event.input_type == const.InputTypes.MOVE and self.controlling is not None and check_movable(self.controlling, self):
            self.controlling.move(event.displacement)
        elif event.input_type == const.InputTypes.ATTACK and self.controlling is not None:
            from model.building import Tower
            if not isinstance(self.controlling, Tower):
                if self.choose_position is True:
                    self.controlling.call_abilities(event.displacement)
                    self.choose_position = False
                elif clicked_tower is not None and clicked == const.CharTypes.TOWER:
                    self.controlling.attack(clicked_tower)
                elif clicked_character is not None and clicked == const.CharTypes.CHAR:
                    self.controlling.attack(clicked_character)
        elif event.input_type == const.InputTypes.ABILITIES and self.controlling is not None:
            from model.building import Tower
            if not isinstance(self.controlling, Tower):
                if isinstance(self.controlling, RangerFighter):
                    self.choose_position = True
                else:
                    self.controlling.call_abilities()

    def gain_character(self, event: EventSpawnCharacter):
        self.character_list.append(event.character)

    def gain_tower(self, event: EventTeamGainTower):
        if event.tower not in self.building_list:
            self.building_list.append(event.tower)
        print(self.name, "gained a tower with id",
              event.tower.id, "at", event.tower.position)

    def lose_tower(self, event: EventTeamLoseTower):
        print(self.name, "lost a tower with id", event.tower.id, "at", event.tower.position)
        if event.tower in self.building_list:
            self.building_list.remove(event.tower)

    def gain_point_kill(self):
        b = 1
        self.points += b
        print(self.name, " gain", b, "points.")

    def gain_point_tower(self, event: EventEveryTick):
        a = 1
        self.points += a * len(self.building_list)
        print(self.name, " gain", a * len(self.building_list), "points.")

    def handle_character_died(self, event: EventCharacterDied):
        if self.controlling is event.character:
            self.controlling = None
        if event.character in self.character_list:
            self.character_list.remove(event.character)
        if event.character in self.visible_entities_list:
            self.visible_entities_list.remove(event.character)

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
                    self.visible_entities_list.add(other_entity)
        else:
            for my_entity in chain(self.building_list, self.character_list):
                if my_entity.alive and entity.position.distance_to(my_entity.position) <= my_entity.vision:
                    self.visible_entities_list.add(entity)
                    break

    def select_character(self, event: EventSelectCharacter):
        if self.controlling is not None and hasattr(self.controlling, 'update_character_type'):
            self.controlling.update_character_type(event.character)
            print(f'The character produced by {self.name} is modified to {event.character}')

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        if self.manual_control:
            ev_manager.register_listener(EventHumanInput, self.handle_input)
        ev_manager.register_listener(EventCreateTower, self.handle_create_tower)
        ev_manager.register_listener(EventTeamGainTower, self.gain_tower, self.id)
        ev_manager.register_listener(EventTeamLoseTower, self.lose_tower, self.id)
        ev_manager.register_listener(EventSpawnCharacter, self.gain_character, self.id)
        ev_manager.register_listener(EventSelectCharacter, self.select_character)
        ev_manager.register_listener(EventCharacterDied, self.handle_character_died)
