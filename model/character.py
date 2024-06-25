import pygame as pg
from instances_manager import get_event_manager
from model.entity import Entity
from event_manager import EventEveryTick, EventInitialize, EventQuit, EventCreateEntity, EventAttack
from model.team import Team


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

    def __init__(self, team: Team, position: pg.Vector2 | tuple[float, float], speed: float, attack_range: float,
                 damage: float, health: float, vision: float, alive: bool = True):
        super().__init__(position)
        self.team = team
        self.speed: float = speed
        self.attack_range: float = attack_range
        self.damage: float = damage
        self.health: float = health
        self.vision: float = vision
        self.alive: bool = alive
        get_event_manager().register_listener(EventAttack, self.take_damage, self.id)

    def move(self, direction: pg.Vector2):
        """
        Move the character in the given direction.
        """
        if direction.length() > self.speed:
            direction = direction.normalize()
            self.position += direction * self.speed

    def take_damage(self, event: EventAttack):
        self.health -= event.attacker.damage
        if self.health <= 0:
            self.die()
        print(f"I received {event.attacker.damage} points of damage")

    def attack(self, enemy):
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team and dist <= self.attack_range):
            get_event_manager().post(EventAttack(self, enemy), enemy.id)
        else:
            print("attack failed")

    def die(self):
        self.alive = False
