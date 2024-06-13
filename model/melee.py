import pygame as pg
from model.character import Character
from const.melee import MELEE_ATTACK_RANGE, MELEE_DAMAGE, MELEE_HEALTH, MELEE_SPEED, MELEE_VISION
from event_manager import EventAttack

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

    def __init__(self, team, position, alive = True, defense = False):
        super().__init__(team, position, MELEE_SPEED, MELEE_ATTACK_RANGE, MELEE_DAMAGE, MELEE_HEALTH, MELEE_VISION, alive)
        self.defense = defense

    def take_damage(self, event: EventAttack):
        if self.defense:
            event.attacker.damage *= 0.5 # set reduced damage to 0.5 of the original one for test
        super(Melee, self).take_damage(event)
    
    def move(self, direction: pg.Vector2):
        if (not self.defense):
            super(Melee, self).move(direction)

    def switch_mode(self):
        self.defense = not self.defense