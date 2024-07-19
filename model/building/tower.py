"""
The module defines Building class.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg
from ordered_set import OrderedSet

import const
from event_manager import (EventAttack, EventBulletCreate, EventCreateTower, EventEveryTick,
                           EventSpawnCharacter, EventTeamGainTower, EventTeamLoseTower)
from instances_manager import get_event_manager, get_model
from model.bullet import BulletCommon
from model.character import Character, Melee, Ranger, Sniper
from model.entity import LivingEntity
from model.timer import Timer

if TYPE_CHECKING:
    from model.model import Model
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

    def __init__(self, position: pg.Vector2, team: Team, tower_type: const.TowerType):
        self.__is_fountain: bool = tower_type is const.TowerType.FOUNTAIN
        self.__tower_type: const.TowerType = tower_type
        self.__character_type: const.CharacterType = const.CharacterType.RANGER
        self.__enemies: OrderedSet[Character] = OrderedSet()
        self.period: float = const.TOWER_SPAWN_INITIAL_PERIOD
        self.last_generate: float = -1e9
        self.__spawn_grids: list[pg.Vector2] = [
            position + pg.Vector2(x, y)
            for x in range(-const.TOWER_GENERATE_DISPLACEMENT, const.TOWER_GENERATE_DISPLACEMENT)
            for y in range(-const.TOWER_GENERATE_DISPLACEMENT, const.TOWER_GENERATE_DISPLACEMENT)
            if ((x*x + y*y <= const.TOWER_GENERATE_DISPLACEMENT ** 2)
                and (get_model().map.get_position_type(position + pg.Vector2(x, y)) != const.MAP_OBSTACLE))
        ]
        """Grids that can spawn characters for this tower."""

        self.attribute: const.TowerAttribute
        if self.__is_fountain:
            super().__init__(position, const.FOUNTAIN_ATTRIBUTE,
                             team, tower_type, invulnerability=True)
        else:
            super().__init__(position, const.NEUTRAL_TOWER_ATTRIBUTE, team, tower_type)

        self.register_listeners()

        self.attack_timer = Timer(1 / self.attribute.attack_speed,
                                  self.attack, once=False)

        if self.team.party is not const.PartyType.NEUTRAL:
            self.last_generate = get_model().get_time()
            get_event_manager().post(EventTeamGainTower(tower=self), self.team.team_id)
        else:
            self.health = const.NEUTRAL_TOWER_ATTRIBUTE.neautral_initial_health
        get_event_manager().post(EventCreateTower(tower=self))

    def __str__(self):
        return f'tower {self.id} (team {self.team.team_id + 1})'

    def update_period(self):
        self.period = const.count_period_ms(len(self.team.character_list))

    def generate_character(self, _: EventEveryTick):
        if self.team.party is const.PartyType.NEUTRAL:
            return
        self.update_period()
        if get_model().get_time() - self.last_generate >= self.period:
            character_type: type[Character]
            if self.__character_type is const.CharacterType.MELEE:
                character_type = Melee
            elif self.__character_type is const.CharacterType.RANGER:
                character_type = Ranger
            elif self.__character_type is const.CharacterType.SNIPER:
                character_type = Sniper
            else:
                raise TypeError(f'Character type error: {self.__character_type}')

            rng = get_model().rng
            new_position = rng.choice(self.__spawn_grids) + \
                pg.Vector2(rng.random(), rng.random())
            new_character = character_type(new_position, self.team)
            self.last_generate = get_model().get_time()
            get_event_manager().post(EventSpawnCharacter(character=new_character), self.team.team_id)

    def update_character_type(self, character_type):
        self.__character_type = character_type

    def take_damage(self, event: EventAttack):
        ev_manager = get_event_manager()

        if not self.vulnerable(event.attacker) or self.team == event.attacker.team:
            return

        if isinstance(event.attacker, Character):
            event.attacker.record_attack(min(self.health, event.damage))
        if self.health - event.damage <= 0:
            if self.team.party is const.PartyType.NEUTRAL:
                ev_manager.post(EventTeamGainTower(tower=self), event.attacker.team.team_id)
            else:
                ev_manager.post(EventTeamLoseTower(tower=self), self.team.team_id)
                ev_manager.post(EventTeamGainTower(tower=self), event.attacker.team.team_id)
            self.team = event.attacker.team
            self.last_generate = get_model().get_time()
            self.update_period()
            self.health = self.attribute.max_health

        else:
            self.health -= event.damage

    def attack(self):
        for character in self.__enemies:
            if character.team != self.team:
                bullet = BulletCommon(position=self.position,
                                      team=self.team,
                                      damage=self.attribute.attack_damage,
                                      victim=character,
                                      speed=const.BULLET_COMMON_SPEED,
                                      attacker=self)
                get_event_manager().post(EventBulletCreate(bullet=bullet))
                break

    def enemy_in_range(self, character: Character):
        if character in self.__enemies or character.position.distance_to(self.position) > self.attribute.attack_range or not character.alive:
            return
        self.__enemies.add(character)

    def enemy_out_range(self, character: Character):
        if character not in self.__enemies:
            return
        if character.position.distance_to(self.position) > self.attribute.attack_range or not character.alive:
            self.__enemies.remove(character)

    def register_listeners(self):
        """Register every listeners of this object into the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.take_damage, self.id)
        ev_manager.register_listener(EventEveryTick, self.generate_character)

    @property
    def is_fountain(self) -> bool:
        return self.__is_fountain

    @property
    def character_type(self) -> const.CharacterType:
        return self.__character_type

    @property
    def tower_type(self) -> const.TowerType:
        return self.__tower_type
