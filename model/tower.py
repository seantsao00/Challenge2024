"""
The module defines Tower class.
"""

import pygame as pg
from model.entity import Entity
from model.building import Building
from instances_manager import get_event_manager
from event_manager import EventAttack, EventTeamGainTower, EventTeamLoseTower

class Tower(Building):
    """
    Class for Tower (object) in the game.
    Each Tower has the following property:
     - health_init: The original health of the tower.
     - health_now: The health of the tower now.
    """

    def __init__(self, health: float, position: pg.Vector2):
        super().__init__(position)
        self.health_init = health
        self.health_now = health
        get_event_manager().register_listener(EventAttack, self.take_damage, self.id)

    def take_damage(self, event: EventAttack):
        if self.health_now - event.attacker.damage <= 0:
            if self.team is None:
                get_event_manager().post(EventTeamGainTower(self.id), event.attacker.team.id)
                self.team = event.attacker.team
            else:
                get_event_manager().post(EventTeamLoseTower(self.id), self.team.id)
                get_event_manager().post(EventTeamGainTower(self.id), event.attacker.team.id)
                self.team = event.attacker.team
            self.spawn_timer.delete()
            self.set_timer()
            self.health_now = self.health_init

        else:
            self.health_now -= event.attacker.damage
        print(self.team, self.health_now)
