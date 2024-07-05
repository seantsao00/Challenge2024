"""
The module defines Building class.
"""

from random import choice, randint

import pygame as pg

import const
import view
from event_manager import (EventAttack, EventCreateTower, EventSpawnCharacter, EventTeamGainTower,
                           EventTeamLoseTower)
from instances_manager import get_event_manager, get_model
from model.building.linked_list import Linked_list, Node
from model.character import Character, Melee, RangerFighter, Sniper
from model.entity import LivingEntity
from model.team import Team
from model.timer import Timer


class Tower(LivingEntity):
    """
    Class for Tower (object) in the game.
    Each Tower has the following property:
     - max_health: The original health of the tower. (from class entity)
     - health: The health of the tower now. (from class entity)
     - id: The id of the entity. (from entity)
     - log: A dictionary log of soldier generation, sorted by time. If the owner changed, the log will clear
     - spawn_timer: The timer spawning characters.
     - character_type: The type chose to generate next, RangerFighter by default.
     - period: The period to generate characters, in milliseconds, integer.
     - is_fountain: is fountion or not.
     - attack_timer: The timer to periodcally attack characters.
    """

    def __init__(self, position: pg.Vector2, team: Team = None, is_fountain: bool = False, entity_type='tower', imgstate='default'):
        super().__init__(const.TOWER_HEALTH, position, const.TOWER_VISION,
                         entity_type=entity_type, team=team, imgstate=imgstate)
        self.log = []
        self.period = const.INITIAL_PERIOD_MS
        self.is_fountain = is_fountain
        self.character_type = RangerFighter
        self.attack_range: float = const.TOWER_ATTACK_RANGE
        self.damage: float = const.TOWER_DAMAGE
        self.enemy: list[Linked_list] = [Linked_list() for _ in range(5)]
        self.spawn_timer = None
        self.attack_timer = Timer(const.tower.TOWER_ATTACK_PERIOD, self.attack, once=False)
        get_event_manager().register_listener(EventAttack, self.take_damage, self.id)
        if self.is_fountain:
            self.imgstate = 'temporary_blue_nexus'
        if self.team is not None:
            self.set_timer()
            get_event_manager().post(EventTeamGainTower(tower=self), self.team.id)
        model = get_model()
        if model.show_view_range:
            self.view.append(view.ViewRangeView(self))
        if model.show_attack_range:
            self.view.append(view.AttackRangeView(self))
        self.view.append(view.TowerCDView(self))
        if self.health is not None and not self.is_fountain:
            self.view.append(view.HealthView(self))
        get_event_manager().post(EventCreateTower(tower=self))

    def update_period(self):
        self.period = const.INITIAL_PERIOD_MS + \
            int(const.FORMULA_K * len(self.team.building_list) ** 0.5)

    def generate_character(self, timestamp=pg.time.get_ticks()):
        character_type = self.character_type
        self.log.append((character_type, timestamp))
        new_position = pg.Vector2(0, 20)
        new_character = character_type(self.team, self.position + new_position)
        get_event_manager().post(EventSpawnCharacter(character=new_character), self.team.id)
        self.set_timer()

    def set_timer(self):
        self.update_period()
        self.spawn_timer = Timer(self.period, self.generate_character, once=True)

    def update_character_type(self, character_type):
        self.character_type = character_type

    def take_damage(self, event: EventAttack):
        if self.team is event.attacker.team or self.is_fountain:
            print("same team or is fountion")
            return
        if self.health - event.attacker.damage <= 0:
            if self.team is None:
                get_event_manager().post(EventTeamGainTower(tower=self), event.attacker.team.id)
            else:
                get_event_manager().post(EventTeamLoseTower(tower=self), self.team.id)
                get_event_manager().post(EventTeamGainTower(tower=self), event.attacker.team.id)
            self.team = event.attacker.team
            self.imgstate = 'team' + str(self.team.id)
            if self.spawn_timer is not None:
                self.spawn_timer.delete()
            self.set_timer()
            self.health = self.max_health

        else:
            self.health -= event.attacker.damage

    def attack(self):
        victim: Node = None
        for i in range(1, 5):
            if (self.team == None or self.team.id != i) and self.enemy[i].front() != None and (victim == None or victim.time > self.enemy[i].front().time):
                victim = self.enemy[i].front()
        if victim != None:
            get_event_manager().post(EventAttack(attacker=self, victim=victim.character), victim.character.id)

    def enemy_in_range(self, character: Character):
        if character.id in self.enemy[character.team.id].map:
            return
        self.enemy[character.team.id].push_back(character, get_model().get_time())

    def enemy_out_range(self, character: Character):
        if character.id not in self.enemy[character.team.id].map:
            return
        self.enemy[character.team.id].delete(character)
