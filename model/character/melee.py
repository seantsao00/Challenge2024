import pygame as pg

import const
from event_manager import EventAttack
from model.character import Character
from model.timer import Timer


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

    def __init__(self, team, position, defense=0):
        super().__init__(position, team, const.MELEE_SPEED, const.MELEE_ATTACK_RANGE,
                         const.MELEE_DAMAGE, const.MELEE_HEALTH, const.MELEE_VISION, const.MELEE_ATTACK_SPEED, const.MELEE_ABILITIES_CD)
        self.defense = defense
        self.imgstate = 'melee'

    def take_damage(self, event: EventAttack):
        if self.defense > 0:
            new_damage = 0.5 * event.attacker.damage
            self.defense -= 1
        else:
            new_damage = event.attacker.damage
        self.health -= new_damage
        if self.health <= 0:
            self.die()

    def move(self, direction: pg.Vector2):
        super().move(direction)

    def abilities(self):
        print("melee use abilites")
        self.defense = const.MELEE_ABILITIES_VARIABLE
