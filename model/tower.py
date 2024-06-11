"""
The module defines Tower class.
"""

import pygame as pg
from model.entity import Entity


class Tower(Entity):
    """
    Class for Tower (object) in the game.
    Each Tower has the following property:
     - health_init: The original health of the tower.
     - health_now: The health of the tower now.
     - id: The id of the tower.
     - damaged: The tower is damaged or not.
     - position: The position of the tower.
    """

    tower_total = 0

    def __init__(self, health: float, position: pg.Vector2):
        super().__init__()
        self.health_init = health
        self.health_now = health
        self.damaged = False
        self.position = position

        self.id = Tower.tower_total + 1
        Tower.tower_total += 1

    def take_damage(self, damage: int):
        if self.health_now - damage <= 0:
            self.health_now = 0
            self.damaged = True
        else:
            self.health_now -= damage
