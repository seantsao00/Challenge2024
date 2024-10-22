from __future__ import annotations

import math
from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventAttack
from instances_manager import get_event_manager, get_model
from model.character.character import Character
from model.entity import Entity
from util import log_info

if TYPE_CHECKING:
    from model.team import Team


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
        super().__init__(position, team, const.MELEE_ATTRIBUTE,
                         const.CharacterType.MELEE, const.CharacterState.LEFT)
        self.__defense: float = 0

    def attack(self, enemy: Entity) -> bool:
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team
            and dist <= self.attribute.attack_range
                and (now_time - self._last_attack_time) * self.attribute.attack_speed >= 1):
            get_event_manager().post(EventAttack(attacker=self, victim=enemy,
                                                 damage=self.attribute.attack_damage), enemy.id)
            self._last_attack_time = now_time
        if dist <= self.attribute.attack_range:
            return True
        return False

    def take_damage(self, event: EventAttack):
        if not self.vulnerable(event.attacker):
            return

        if self.__defense > 0:
            new_damage = 0.5 * event.damage
            self.__defense -= 1
            if self.__defense == 0:
                self.abilities_time = get_model().get_time()
                if const.AscendanceType.ARMOR in self.ascendance:
                    self.ascendance.remove(const.AscendanceType.ARMOR)
        else:
            new_damage = event.damage
        self.health -= new_damage
        if event.attacker.entity_type is const.CharacterType.MELEE or\
           event.attacker.entity_type is const.CharacterType.RANGER or\
           event.attacker.entity_type is const.CharacterType.SNIPER:
            event.attacker.record_attack(min(self.health, event.damage))
        if self.health <= 0:
            self.die()
            if event.attacker.team.party is not const.PartyType.NEUTRAL:
                event.attacker.team.gain_point_kill()
                log_info(
                    f"[Team] {event.attacker.team.team_name} get score, score is {event.attacker.team.points}")

    def cast_ability(self, *args, **kwargs):
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.attribute.ability_cd:
            return
        log_info(f"[Melee] {self} Cast ability")
        self.abilities_time = now_time
        self.ascendance.add(const.AscendanceType.ARMOR)
        self.ability()

    def manual_cast_ability(self, *args, **kwargs):
        self.cast_ability(*args, **kwargs)

    def ability(self):
        self.__defense = const.MELEE_ATTRIBUTE.ability_variables
        self.abilities_time = math.inf
        # ability will disappear after the melee is hit self.__defense times.
