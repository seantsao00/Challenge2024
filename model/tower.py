"""
The module defines Tower class.
"""

import pygame as pg
from model.entity import Entity
from model.building import Building

class Tower(Building):
    """
    Class for Tower (object) in the game.
    Each Tower has the following property:
     - health_init: The original health of the tower.
     - health_now: The health of the tower now.
     - damaged: The tower is damaged or not.
     - position: The position of the tower.
    """

    def __init__(self, health: float, position: pg.Vector2):
        super().__init__(position)
        self.health_init = health
        self.health_now = health
        self.position = position

    def take_damage(self, damage: int):
        if self.health_now - damage <= 0:
            pass
        else:
            self.health_now -= damage
