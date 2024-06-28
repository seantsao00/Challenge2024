"""
The module defines Building class.
"""

from random import choice, randint

import pygame as pg

import const
import const.tower
import view
from event_manager import (EventAttack, EventSpawnCharacter,
                           EventTeamGainTower, EventTeamLoseTower)
from instances_manager import get_event_manager, get_model
from model.character import Character, Melee
from model.entity import Entity
from model.team import Team
from model.timer import Timer


class Tower(Entity):
    """
    Class for Tower (object) in the game.
    Each Tower has the following property:
     - max_health: The original health of the tower. (from class entity)
     - health: The health of the tower now. (from class entity)
     - id: The id of the entity. (from entity)
     - log: A dictionary log of soldier generation, sorted by time. If the owner changed, the log will clear
     - spawn_timer: The timer spawning characters.
     - character_type: The type chose to generate next, melee by default.
     - period: The period to generate characters, in milliseconds, integer.
     - is_fountain: is fountion or not.
     - attack_timer: The timer to periodcally attack characters.
    """

    def __init__(self, position: pg.Vector2, team: Team = None, is_fountain: bool = False, entity_type='tower', imgstate='default'):
        super().__init__(position, health=const.TOWER_HEALTH,
                         entity_type=entity_type, team=team, imgstate=imgstate)
        self.log = []
        self.period = const.tower.INITIAL_PERIOD_MS
        self.is_fountain = is_fountain
        self.character_type = Melee
        self.attack_range: float = const.TOWER_ATTACK_RANGE
        self.damage: float = const.TOWER_DAMAGE
        self.vision: float = const.TOWER_VISION
        self.spawn_timer = None
        if not is_fountain:
            self.attack_timer = Timer(const.tower.TOWER_ATTACK_PERIOD, self.attack, once=False)
        else:
            self.attack_timer = None
        get_event_manager().register_listener(EventAttack, self.take_damage, self.id)
        if self.is_fountain:
            self.imgstate = 'temporary_blue_nexus'
        if self.team is not None:
            self.set_timer()
            get_event_manager().post(EventTeamGainTower(self), self.team.id)
        model = get_model()
        if model.show_view_range:
            self.view.append(view.ViewRangeView(self))
        if model.show_attack_range:
            self.view.append(view.AttackRangeView(self))
        if self.health is not None and not self.is_fountain:
            self.view.append(view.HealthView(self))

    def update_period(self):
        self.period = const.tower.INITIAL_PERIOD_MS + \
            int(const.tower.FORMULA_K * len(self.team.building_list) ** 0.5)

    def generate_character(self, character_type: Character, timestamp=pg.time.get_ticks()):
        self.log.append((character_type, timestamp))
        new_position = pg.Vector2(
            choice([1, -1]) * (50 + randint(-50, 50)), choice([1, -1]) * (50 + randint(-50, 50)))
        new_character = character_type(self.team, self.position + new_position)
        get_event_manager().post(EventSpawnCharacter(new_character), self.team.id)
        self.set_timer()

    def set_timer(self):
        self.update_period()
        self.spawn_timer = Timer(self.period, self.generate_character,
                                 self.character_type, once=True)

    def update_character_type(self, character_type):
        self.character_type = character_type

    def take_damage(self, event: EventAttack):
        if self.team is event.attacker.team or self.is_fountain:
            print("same team or is fountion")
            return
        if self.health - event.attacker.damage <= 0:
            if self.team is None:
                get_event_manager().post(EventTeamGainTower(self), event.attacker.team.id)
            else:
                get_event_manager().post(EventTeamLoseTower(self), self.team.id)
                get_event_manager().post(EventTeamGainTower(self), event.attacker.team.id)
            self.team = event.attacker.team
            self.imgstate = 'team' + str(self.team.id)
            self.set_timer()
            self.health = self.max_health

        else:
            self.health -= event.attacker.damage
        print(self.team, self.health)

    def attack(self):
        model = get_model()
        nearest_characters = model.grid.get_nearest_characters(self.position, 100)
        for character in nearest_characters:
            if character.team != self.team:
                get_event_manager().post(EventAttack(self, character), character.id)
                break
