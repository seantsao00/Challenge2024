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
from model.building.linked_list import LinkedList, Node
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

    def __init__(self, position: pg.Vector2, team: Team, is_fountain: bool = False):
        self.__period = const.INITIAL_PERIOD_MS
        self.__is_fountain = is_fountain
        self.__character_type: const.CharacterType = const.CharacterType.RANGER
        self.__enemies: list[LinkedList] = [LinkedList() for _ in range(4)]
        self.spawn_timer: Timer | None = None

        if is_fountain:
            super().__init__(position, const.FOUNTAIN_ATTRIBUTE, team, const.TowerType.FOUNTAIN)
        else:
            super().__init__(position, const.NEUTRAL_TOWER_ATTRIBUTE, team, const.TowerType.HOTEL)

        self.register_listeners()

        self.attack_timer = Timer(int(1 / self.attribute.attack_speed * 1000),
                                  self.attack, once=False)

        if self.team.party is not const.PartyType.NEUTRAL:
            self.set_timer()
            get_event_manager().post(EventTeamGainTower(tower=self), self.team.team_id)
        get_event_manager().post(EventCreateTower(tower=self))

    def update_period(self):
        self.__period = const.INITIAL_PERIOD_MS + \
            int(const.FORMULA_K * len(self.team.towers) ** 0.5)

    def generate_character(self):
        character_type: Type[Character]
        if self.__character_type is const.CharacterType.MELEE:
            character_type = Melee
        elif self.__character_type is const.CharacterType.RANGER:
            character_type = Ranger
        elif self.__character_type is const.CharacterType.SNIPER:
            character_type = Sniper
        else:
            raise TypeError(f'Character type error: {self.__character_type}')
        new_position = pg.Vector2()
        new_position.from_polar((random.uniform(0, 10), random.uniform(0, 360)))
        new_character = character_type(self.position + new_position, self.team)
        get_event_manager().post(EventSpawnCharacter(character=new_character), self.team.team_id)
        self.set_timer()

    def set_timer(self):
        self.update_period()
        self.spawn_timer = Timer(self.__period, self.generate_character, once=True)

    def update_character_type(self, character_type):
        self.__character_type = character_type

    def take_damage(self, event: EventAttack):
        ev_manager = get_event_manager()
        if self.team is event.attacker.team or self.is_fountain:
            print('same team or is fountain')
            return
        if self.health - event.attacker.attribute.attack_damage <= 0:
            if self.team.party is const.PartyType.NEUTRAL:
                ev_manager.post(EventTeamGainTower(tower=self), event.attacker.team.team_id)
            else:
                ev_manager.post(EventTeamLoseTower(tower=self), self.team.team_id)
                ev_manager.post(EventTeamGainTower(tower=self), event.attacker.team.team_id)
            self.team = event.attacker.team
            if self.spawn_timer is not None:
                self.spawn_timer.delete()
            self.set_timer()
            self.health = self.attribute.max_health

        else:
            self.health -= event.attacker.attribute.attack_damage

    def attack(self):
        victim: Node | None = None
        for i in range(0, 4):
            if ((self.team.party is const.PartyType.NEUTRAL or self.team.team_id != i)
                and self.__enemies[i].front() is not None
                    and (victim is None or victim.time > self.__enemies[i].front().time)):
                victim = self.__enemies[i].front()
        if victim is not None:
            get_event_manager().post(EventAttack(attacker=self, victim=victim.character), victim.character.id)

    def enemy_in_range(self, character: Character):
        if (character.id in self.__enemies[character.team.team_id].map
            or character.position.distance_to(self.position) > self.attribute.attack_range
                or not character.alive):
            return
        # print(character.type, 'get in tower')
        self.__enemies[character.team.team_id].push_back(character, get_model().get_time())

    def enemy_out_range(self, character: Character):
        if character.id not in self.__enemies[character.team.team_id].map:
            return
        if character.position.distance_to(self.position) > self.attribute.attack_range or not character.alive:
            # print(character.type, 'get out of tower')
            self.__enemies[character.team.team_id].delete(character)

    def register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.take_damage, self.id)

    @property
    def is_fountain(self) -> bool:
        return self.__is_fountain
