import pygame as pg
import const
import const.team
from model.entity import Entity
from instances_manager import get_event_manager
from event_manager import EventTeamGainTower, EventTeamLoseTower, EventHumanInput


class Team:

    """
    Class for Team in the game.
    Each Team has the following property:
     - name: The name of the team.
     - master: The controller of the team.
     - total_towers: The total towers that this team has.
     - points: The accumulated points of the team.
     - id: The id of the team.
     - fountain: The fountain of the team
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

    def set_fountain(self, fountain):
        self.fountain = fountain

    def gain_tower(self, event: EventTeamGainTower):
        self.total_buildings += 1
        print(self.id, " Gained a tower")

    def lose_tower(self, event: EventTeamLoseTower):
        print(self.id, " Lost a tower")
        self.total_buildings -= 1
