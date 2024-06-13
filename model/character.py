import pygame as pg
from instances_manager import get_event_manager
from model.entity import Entity
from event_manager import EventEveryTick, EventInitialize, EventPlayerMove, EventQuit, EventCreateEntity, EventAttack
class Character(Entity):
    """
    Class for character in the game.
    Each character has the following property:
     - speed: How fast the character moves in the game.
     - attack_range: How far the character can attack.
     - damage: How much hurt the character can cause in one attack.
     - health: The total amount of damage the character can withstand.
     - vision: How far the character can see.
     - alive: The character is alive or not.
    """

    def __init__(self, team, position, speed, attack_range, damage, health, vision, alive = True):
        super().__init__(position)
        self.team = team
        self.speed = speed
        self.attack_range = attack_range
        self.damage = damage
        self.health = health
        self.vision = vision
        self.alive = alive
    
    def move(self, direction: pg.Vector2):
        """
        Move the character in the given direction.
        """
        if direction.length() > self.speed:
            direction = direction.normalize()
            self.position += direction * self.speed
    
    def take_damage(self, damage: int):
        self.health -= damage
        if self.health <= 0:
            self.die()
        print(f"I received {damage} points of damage")

    def attack(self, enemy):
        get_event_manager().post(EventAttack(self, enemy))

    def die(self):
        self.alive = False

