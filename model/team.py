from __future__ import annotations

from typing import TYPE_CHECKING

from itertools import chain
import pygame as pg

import const
import const.team
from event_manager import (EventEveryTick, EventHumanInput,
                           EventSpawnCharacter, EventTeamGainTower,
                           EventTeamLoseTower)
from instances_manager import get_event_manager, get_model

if TYPE_CHECKING:
    from model.building import Tower
    from model.entity import Entity
    from model.character import Character


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

    def __init__(self, fountain_position: pg.Vector2, name: str, master: str):
        if Team.total == 4:
            raise Exception('Team size exceeds.')
        Team.total += 1
        self.id = Team.total
        self.name = name
        self.points = 0
        self.master = master
        self.building_list: list[Tower] = []
        self.character_list: list[Character] = []
        self.visible_entities_list: list[Entity] = []
        if master == 'human':
            self.controlling = None
            get_event_manager().register_listener(EventHumanInput, self.handle_input)
        get_event_manager().register_listener(EventTeamGainTower, self.gain_tower, self.id)
        get_event_manager().register_listener(EventTeamLoseTower, self.lose_tower, self.id)
        get_event_manager().register_listener(EventSpawnCharacter, self.gain_character, self.id)

    def handle_input(self, event: EventHumanInput):
        """
        Handles input by human. This method is only used by human controlled teams.
        """
        def check_interactable(entity: Entity, my_team: Team):
            """
            This function checks if the clicked entity is actually interactable by the human controlled team.
            Any new interactive feature implementation should modify this function.
            """
            if entity is None:
                return False
            if hasattr(entity, 'team') and entity.team is my_team and hasattr(entity, 'move'):
                return True
            return False

        if event.input_type == const.InputTypes.PICK:
            if check_interactable(event.clicked, self):
                self.controlling = event.clicked
            else:
                print('clicked on non interactable entity')
        elif event.input_type == const.InputTypes.MOVE and self.controlling is not None:
            self.controlling.move(event.displacement)
        elif event.input_type == const.InputTypes.ATTACK and self.controlling is not None and event.clicked is not None:
            self.controlling.attack(event.clicked)

    def gain_character(self, event: EventSpawnCharacter):
        self.character_list.append(event.character)

    def gain_tower(self, event: EventTeamGainTower):
        if event.tower not in self.building_list:
            self.building_list.append(event.tower)
        print(self.id, " gained a tower with id",
              event.tower.id, " at", event.tower.position)

    def lose_tower(self, event: EventTeamLoseTower):
        print(self.id, " lost a tower with id", event.tower.id, " at", event.tower.position)
        if event.tower in self.building_list:
            self.building_list.remove(event.tower)

    def gain_point_kill(self):
        b = 1
        self.points += b
        print(self.id, " gain", b, "points.")

    def gain_point_tower(self, event: EventEveryTick):
        a = 1
        self.points += a * self.total_buildings
        print(self.id, " gain", a * self.total_buildings, "points.")

    def update_visible_entities_list(self):
        """
        This function updates the current entities visible to the instance of Team.
        Still looking for a better algorithm to implement this feature.
        """
        model = get_model()
        
        self.visible_entities_list = []
        for entity in model.entities:
            if entity.team is not self:
                for my_entity in chain(self.building_list, self.character_list):
                    if my_entity.alive and my_entity.position.distance_to(entity.position) <= my_entity.vision:
                        self.visible_entities_list.append(entity)
                        break
