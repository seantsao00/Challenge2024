import pygame as pg
import const
import const.team
from instances_manager import get_event_manager
from event_manager import EventTeamGainTower, EventTeamLoseTower

class Team:

    """
    Class for Team in the game.
    Each Team has the following property:
     - spring_position: The original position of the spring.
     - name: The name of the team.
     - total_towers: The total towers that this team has.
     - points: The accumulated points of the team.
     - id: The id of the team.
     - gen_gap: The time gap to generate a new character. 
    """

    total = 0

    def __init__(self, spring_position: pg.Vector2, name: str):
        if Team.total == 4:
            raise Exception('Team size exceeds.')
        self.spring_position = spring_position
        self.name = name
        self.total_towers = 0
        self.points = 0
        self.id = Team.total + 1
        self.gen_gap = const.GENERATE_GAP
        Team.total += 1
        get_event_manager().register_listener(EventTeamGainTower, self.gain_tower, self.id)
        get_event_manager().register_listener(EventTeamLoseTower, self.lose_tower, self.id)


    def gain_tower(self, event: EventTeamGainTower):
        self.total_towers += 1
        print(self.id, " Gained a tower")

    def lose_tower(self, event: EventTeamLoseTower):
        print(self.id, " Lost a tower")
        self.total_towers -= 1