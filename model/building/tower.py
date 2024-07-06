"""
The module defines Building class.
"""
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Type

import pygame as pg

import const
from event_manager import (EventAttack, EventCreateTower, EventSpawnCharacter, EventTeamGainTower,
                           EventTeamLoseTower)
from instances_manager import get_event_manager, get_model
from model.building.linked_list import Linked_list, Node
from model.character import Melee, Ranger, Sniper
from model.entity import LivingEntity
from model.timer import Timer

if TYPE_CHECKING:
    from model.character import Character
    from model.team import Team


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

    def __init__(self, position: pg.Vector2, team: Team = None, is_fountain: bool = False):
        self.__log: list[tuple] = []
        self.__period = const.INITIAL_PERIOD_MS
        self.__is_fountain = is_fountain
        self.__character_type: const.CharacterType = const.CharacterType.RANGER
        self.enemy: list[Linked_list] = [Linked_list() for _ in range(4)]
        self.spawn_timer = None
        if is_fountain:
            super().__init__(position, const.FOUNTAIN_ATTRIBUTE, team, const.TowerType.FOUNTAIN)
        else:
            super().__init__(position, const.NEUTRAL_TOWER_ATTRIBUTE, team, const.TowerType.HOTEL)
        self.attack_timer = Timer(1/self.attack_speed, self.attack, once=False)
        self.register_listeners()

        if self.__team is not None:
            self.set_timer()
            get_event_manager().post(EventTeamGainTower(tower=self), self.__team.id)
        get_event_manager().post(EventCreateTower(tower=self))

    def update_period(self):
        self.__period = const.INITIAL_PERIOD_MS + \
            int(const.FORMULA_K * len(self.__team.towers) ** 0.5)

    def generate_character(self, timestamp=pg.time.get_ticks()):
        if self.__character_type is const.CharacterType.MELEE:
            character_type = Melee
        elif self.__character_type is const.CharacterType.RANGER:
            character_type = Ranger
        elif self.__character_type is const.CharacterType.SNIPER:
            character_type = Sniper
        self.__log.append((self.__character_type, timestamp))
        new_position = pg.Vector2()
        new_position.from_polar(random.uniform(0, 10), random.uniform(0, 360))
        new_character = character_type(self.__team, self.__position + new_position)
        get_event_manager().post(EventSpawnCharacter(character=new_character), self.__team.id)
        self.set_timer()

    def set_timer(self):
        self.update_period()
        self.spawn_timer = Timer(self.__period, self.generate_character, once=True)

    def update_character_type(self, character_type):
        self.__character_type = character_type

    def take_damage(self, event: EventAttack):
        ev_manager = get_event_manager()
        if self.__team is event.attacker.team or self.__is_fountain:
            print('same team or is fountain')
            return
        if self.health - event.attacker.attack_damage <= 0:
            if self.__team is None:
                ev_manager.post(EventTeamGainTower(tower=self), event.attacker.team.id)
            else:
                ev_manager.post(EventTeamLoseTower(tower=self), self.__team.id)
                ev_manager.post(EventTeamGainTower(tower=self), event.attacker.team.id)
            self.__team = event.attacker.team
            if self.spawn_timer is not None:
                self.spawn_timer.delete()
            self.set_timer()
            self.health = self.max_health

        else:
            self.health -= event.attacker.attack_damage

    def attack(self):
        victim: Node = None
        for i in range(0, 4):
            if (self.__team is None or self.__team.id != i) and self.enemy[i].front() != None and (victim == None or victim.time > self.enemy[i].front().time):
                victim = self.enemy[i].front()
        if victim is not None:
            get_event_manager().post(EventAttack(attacker=self, victim=victim.character), victim.character.id)

    def enemy_in_range(self, character: Character):
        if character.id in self.enemy[character.team.id].map or \
           character.position.distance_to(self.__position) > self.attack_range or \
           character.alive is False:
            return
        # print(character.type, 'get in tower')
        self.enemy[character.team.id].push_back(character, get_model().get_time())

    def enemy_out_range(self, character: Character):
        if character.id not in self.enemy[character.team.id].map:
            return
        if character.position.distance_to(self.__position) > self.attack_range or character.alive is False:
            # print(character.type, 'get out of tower')
            self.enemy[character.team.id].delete(character)

    def register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.take_damage, self.__id)
