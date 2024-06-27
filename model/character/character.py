import pygame as pg

import view
from event_manager import (EventAttack, EventCreateEntity, EventEveryTick,
                           EventInitialize, EventQuit)
from instances_manager import get_event_manager, get_model
from model.entity import Entity
from model.team import Team


class Character(Entity):
    """
    Class for character in the game.
    Each character has the following property:
     - speed: How fast the character moves in the game.
     - attack_range: How far the character can attack.
     - damage: How much hurt the character can cause in one attack.
     - max_health: The maximum total health 
     - health: The total amount of damage the character can withstand.
     - vision: How far the character can see.
     - alive: The character is alive or not.
    """

    def __init__(self, team: Team, position: pg.Vector2 | tuple[float, float], speed: float, attack_range: float,
                 damage: float, health: float, vision: float, alive: bool = True):
        super().__init__(position, health)
        self.team = team
        self.speed: float = speed
        self.attack_range: float = attack_range
        self.damage: float = damage
        self.vision: float = vision
        self.alive: bool = alive
        model = get_model()
        if model.show_view_range:
            self.view.append(view.ViewRangeView(self))
        if model.show_attack_range:
            self.view.append(view.AttackRangeView(self))
        if self.health != None:
            self.view.append(view.HealthView(self))
        get_event_manager().register_listener(EventAttack, self.take_damage, self.id)

    def move(self, direction: pg.Vector2):
        """
        Move the character in the given direction.
        """
        if direction.length() != 0:
            direction = direction.normalize()
            self.position += direction * self.speed

    def take_damage(self, event: EventAttack):
        self.health -= event.attacker.damage
        if self.health <= 0:
            self.die()
        print(f"I received {event.attacker.damage} points of damage")

    def attack(self, enemy: Entity):
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team and dist <= self.attack_range):
            get_event_manager().post(EventAttack(self, enemy), enemy.id)
        else:
            print("attack failed")

    def die(self):
        self.alive = False
