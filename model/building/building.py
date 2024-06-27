"""
The module defines Building class.
"""

from random import choice, randint

import pygame as pg

import const
import const.building
from event_manager import EventSpawnCharacter
from instances_manager import get_event_manager
from model.character import Character, Melee
from model.entity import Entity
from model.team import Team
from model.timer import Timer


class Building(Entity):
    """
    Class for Building (object) in the game.
    Each Building has the following property:
    - team: The owner of this building
    - building_id: The id of the building. (Try not to get confused with the id in Entity)
    - log: A dictionary log of soldier generation, sorted by time. If the owner changed, the log will clear
    - spawn_timer: The timer spawning characters.
    - character_type: The type chose to generate next, melee by default.
    - period: The period to generate characters, in milliseconds, integer.
    """

    building_total = 0

    def __init__(self, position: pg.Vector2, team: Team = None, entity_type='default', imgstate='default'):
        super().__init__(position, entity_type, imgstate)
        self.team = team
        self.building_id = Building.building_total + 1
        self.log = []
        self.period = const.building.INITIAL_PERIOD_MS
        self.character_type = Melee
        self.spawn_timer: Timer | None = None
        Building.building_total += 1

    def update_period(self):
        self.period = const.building.INITIAL_PERIOD_MS + \
            int(const.building.FORMULA_K * self.team.total_buildings ** 0.5)

    def generate_character(self, character_type: Character, timestamp=pg.time.get_ticks()):
        self.log.append((character_type, timestamp))
        new_position = pg.Vector2(
            choice([1, -1]) * (200 + randint(-50, 50)), choice([1, -1]) * (200 + randint(-50, 50)))
        new_character = character_type(self.team, self.position + new_position)
        get_event_manager().post(EventSpawnCharacter(new_character), self.team.id)
        self.set_timer()

    def set_timer(self):
        self.update_period()
        self.spawn_timer = Timer(self.period, self.generate_character,
                                 self.character_type, once=True)

    def update_character_type(self, character_type):
        self.character_type = character_type
