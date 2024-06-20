"""
The module defines Tower class.
"""

import pygame as pg
from model.entity import Entity
from model.melee import Melee
from model.lookout import Lookout
from model.ranged import RangedFighter

class Building(Entity):
    """
    Class for Building (object) in the game.
    Each Building has the following property:
     - team: The owner of this building
     - building_id: The id of the building. (Try not to get confused with the id in Entity)
     - position: The position of the building.
    """

    building_total = 0

    def __init__(self, position: pg.Vector2, team=None):
        super().__init__(position)
        self.team = team
        self.building_id = Building.building_total + 1
        Building.building_total += 1

    def generate_soldier(self, character_type):
        if self.team is not None:
            return character_type(self.team, self.position)
        else:
            return None