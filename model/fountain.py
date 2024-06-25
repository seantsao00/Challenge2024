"""
The module defines Tower class.
"""

import pygame as pg
from model.entity import Entity
from model.building import Building
from event_manager import EventAttack
from model.team import Team


class Fountain(Building):
    """
    Class for Fountain (object) in the game.
    Each Building has the following property:
     - team: The owner of this building
     - building_id: The id of the building. (Try not to get confused with the id in Entity)
     - log: A dictionary log of soldier generation, sorted by time. If the owner changed, the log will clear
     - spawn_timer: The timer spawning characters.
     - character_type: The type chose to generate next, melee by default.
     - period: The period to generate characters, in milliseconds, integer.
    """

    def __init__(self, position: pg.Vector2, team: Team):
        super().__init__(position, type='fountain', imgstate='temporary_blue_nexus', team=team)
        self.team.total_buildings += 1
        self.set_timer()

    def take_damage(self, event: EventAttack):
        print(f"Building id:{self.building_id} is a fountain, nothing happened with the attack.")
        return
