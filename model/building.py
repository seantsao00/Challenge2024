"""
The module defines Tower class.
"""

import pygame as pg
from model.entity import Entity


class Building(Entity):
    """
    Class for Building (object) in the game.
    Each Building has the following property:
     - team: The owner of this building
     - id: The id of the building.
     - position: The position of the building.
    """

    building_total = 0

    def __init__(self, team=None, position: pg.Vector2):
        super().__init__(position)
        self.team = team
        self.position = position
        self.id = Building.tower_total + 1
        Building.tower_total += 1
    def generate_soldier():
        if self.team is not None:
            pass