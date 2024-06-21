"""
The module defines Tower class.
"""

import const.building
import pygame as pg
import const
from event_manager import EventEveryTick, EventInitialize, EventPlayerMove, EventQuit, EventCreateEntity, EventAttack, EventMultiAttack
from model.entity import Entity
from model.melee import Melee
from model.lookout import Lookout
from model.ranged_fighter import RangedFighter

class Building(Entity):
    """
    Class for Building (object) in the game.
    Each Building has the following property:
     - team: The owner of this building
     - building_id: The id of the building. (Try not to get confused with the id in Entity)
     - position: The position of the building.
     - log: A dictionary log of soldier generation, sorted by time. If the owner changed, the log will clear
    """

    building_total = 0

    def __init__(self, position: pg.Vector2, team=None, type='default', imgstate='default'):
        super().__init__(position, type, imgstate)
        self.team = team
        self.building_id = Building.building_total + 1
        self.log = list()
        self.period=const.building.INITIAL_PERIOD
        Building.building_total += 1
    def update_period(self):
        pass
    def generate_soldier(self, character_type, timestamp):
        if self.team is not None and ( len(self.log) == 0 or timestamp-self.log[-1]>=self.period):
            self.log.append((character_type,timestamp))
            return character_type(self.team, self.position)
        else:
            return None