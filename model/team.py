import pygame as pg
import const
import const.team

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
        if total == 4:
            raise Exception('Team size exceeds.')
        self.spring_position = spring_position
        self.name = name
        self.total_towers = 0
        self.points = 0
        self.id = total + 1
        self.gen_gap = const.GENERATE_GAP
        total += 1
