import pygame as pg

import const
import const.team
from event_manager import (EventHumanInput, EventTeamGainTower,
                           EventTeamLoseTower)
from instances_manager import get_event_manager
from event_manager import EventTeamGainTower, EventTeamLoseTower, EventHumanInput, EventSpawnCharacter
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model.fountain import Fountain

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
    """

    total = 0

    def __init__(self, fountain_position: pg.Vector2, name: str, master: str):
        if Team.total == 4:
            raise Exception('Team size exceeds.')
        self.name = name
        self.total_buildings = 0
        self.points = 0
        self.id = Team.total + 1
        self.master = master
        self.building_list = []
        self.character_list = []
        if master == 'human':
            self.controlling = None
            get_event_manager().register_listener(EventHumanInput, self.handle_input)
        Team.total += 1
        get_event_manager().register_listener(EventTeamGainTower, self.gain_tower, self.id)
        get_event_manager().register_listener(EventTeamLoseTower, self.lose_tower, self.id)

    def handle_input(self, event: EventHumanInput):
        """
        Handles input by human. This method is only used by human controlled teams.
        """
        def check_interactable(entity: Entity, my_team: Team):
            """
            This function checks if the clicked entity is actually interactable by the human controlled team.
            Any new interactive feature implementation should modify this function.
            """
            if entity == None:
                return False
            elif hasattr(entity, 'team') and entity.team == my_team and hasattr(entity, 'move'):
                return True
            else:
                return False

        if event.input_type == const.INPUT_TYPES.PICK:
            if check_interactable(event.clicked, self):
                self.controlling = event.clicked
            else:
                print('clicked on non interactable entity')
        elif event.input_type == const.INPUT_TYPES.MOVE and self.controlling != None:
            self.controlling.move(event.displacement)
        elif event.input_type == const.INPUT_TYPES.ATTACK and self.controlling != None:
            self.controlling.attack(event.clicked)

    def set_fountain(self, fountain: Fountain):
        self.building_list.append(fountain)

    def gain_character(self, event: EventSpawnCharacter):
        self.character_list.append(event.character)

    def gain_tower(self, event: EventTeamGainTower):
        self.total_buildings += 1
        if event.tower not in self.building_list:
            self.building_list.append(event.tower)
        print(self.id, " gained a tower with id", event.tower.building_id," at", event.tower.position)

    def lose_tower(self, event: EventTeamLoseTower):
        print(self.id, " lost a tower with id", event.tower.building_id," at", event.tower.position)
        if event.tower in self.building_list:
            self.building_list.remove(event.tower)
        self.total_buildings -= 1
