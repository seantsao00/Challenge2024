from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventAttack
from instances_manager import get_event_manager, get_model
from model.character.character import Character
from util import log_info

if TYPE_CHECKING:
    from model.team import Team

from event_manager import EventAttack
from instances_manager import get_event_manager, get_model
from model.entity import Entity


class Melee(Character):
    """

    Class for melee character in the game.
    Each melee has the following property:
     - speed: How fast the character moves in the game. Set to default const value during constructing.
     - attack_range: How far the character can attack. Set to default const value during constructing.
     - damage: How much hurt the character can cause in one attack. Set to default const value during constructing.
     - health: The total amount of damage the character can withstand. Set to default const value during constructing.
     - vision: How far the character can see. Set to default const value during constructing.
     - alive: The character is alive or not.
     - defense: Special power of melee that reduce the damage it takes but it becomes immobile, not using the power when first constructed

    """

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team):
        super().__init__(position, team, const.MELEE_ATTRIBUTE, const.CharacterType.MELEE, None)
        self.__defense: float = 0

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team
            and dist <= self.attribute.attack_range
                and (now_time - self._attack_time) * self.attribute.attack_speed >= 1):
            get_event_manager().post(EventAttack(attacker=self, victim=enemy,
                                                 damage=self.attribute.attack_damage), enemy.id)
            self._attack_time = now_time

    def take_damage(self, event: EventAttack):
        if self.__defense > 0:
            new_damage = 0.5 * event.attacker.attribute.attack_damage
            self.__defense -= 1
            if self.__defense == 0:
                self.abilities_time = get_model().get_time()
        else:
            new_damage = event.attacker.attribute.attack_damage
        self.health -= new_damage
        if self.health <= 0:
            self.die()

    def cast_ability(self, *args, **kwargs):
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.attribute.ability_cd:
            return
        log_info("Melee Cast ability")
        self.abilities_time = now_time
        self.ability()

    def ability(self):
        self.__defense = const.MELEE_ATTRIBUTE.ability_variables
        self.abilities_time = 1e9
