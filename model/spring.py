"""
The module defines Tower class.
"""

import pygame as pg
from model.entity import Entity
from model.building import Building
from event_manager import EventAttack

class Spring(Building):
    """
    Class for Sprint (object) in the game.
    Each Tower has the following property:
     - ?: ???
    """

    def __init__(self, health: float, position: pg.Vector2):
        super().__init__(position, type='fountain', imgstate='temporary_blue_nexus')
    def take_damage(self, event: EventAttack):
        print(f"Tower No. {self.building_id} is a spring, nothing happened.")
        return