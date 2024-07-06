from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventAttack
from model.character.character import Character

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
        super().__init__(position, team, const.MELEE_ATTRIBUTE, None)
        self.defense: float = 0

    def take_damage(self, event: EventAttack):
        if self.defense > 0:
            new_damage = 0.5 * event.attacker.attack_damage
            self.defense -= 1
        else:
            new_damage = event.attacker.attack_damage
        self.health -= new_damage
        if self.health <= 0:
            self.die()

    def ability(self, *args, **kwargs):
        self.defense = const.MELEE_ATTRIBUTE.ability_variables
