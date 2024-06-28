import pygame as pg

import const
import const.map
import util
import view
from event_manager import EventAttack
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

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team, speed: float,
                 attack_range: float, damage: float, health: float, vision: float):
        super().__init__(position, health=health, entity_type='team' + str(team.id), team=team)
        self.speed: float = speed
        self.attack_range: float = attack_range
        self.damage: float = damage
        self.vision: float = vision
        self.alive: bool = True
        model = get_model()
        if model.show_view_range:
            self.view.append(view.ViewRangeView(self))
        if model.show_attack_range:
            self.view.append(view.AttackRangeView(self))
        if self.health is not None:
            self.view.append(view.HealthView(self))
        get_event_manager().register_listener(EventAttack, self.take_damage, self.id)

    def move(self, direction: pg.Vector2):
        """
        Move the character in the given direction.
        """
        if direction.length() > self.speed:
            direction = self.speed * direction.normalize()

        map = get_model().map

        # set the minimum move into 1/4 of the original direction
        min_direction = direction / 4
        cur_direction = direction / 4

        # try further distance
        for i in range(4):

            new_position = self.position + cur_direction
            new_position.x = util.clamp(new_position.x, 0, const.ARENA_SIZE[0] - 1)
            new_position.y = util.clamp(new_position.y, 0, const.ARENA_SIZE[1] - 1)

            # prevent out of bound, in a stupid way
            if (new_position.x + const.ENTITY_RADIUS >= const.ARENA_SIZE[0] or 
                new_position.y + const.ENTITY_RADIUS >= const.ARENA_SIZE[1] or 
                new_position.y - const.ENTITY_RADIUS - const.HEALTH_BAR_UPPER < 0 or
                new_position.x - const.ENTITY_RADIUS < 0):
                self.position += cur_direction - min_direction
                return
            
            if (map.get_type(new_position) == const.map.MAP_OBSTACLE):
                self.position = new_position - min_direction
                return
            
            if (i == 3): 
                self.position = new_position
                return

            cur_direction += min_direction

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
        print("Died")
        get_model().characters.remove(self)
        self.alive = False
        self.hidden = True
