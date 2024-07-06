from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import util
from event_manager import EventAttack, EventCharacterDied, EventCharacterMove, EventEveryTick
from instances_manager import get_event_manager, get_model
from model.entity import LivingEntity

if TYPE_CHECKING:
    from model.entity import Entity
    from model.team import Team


class Character(LivingEntity):
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

    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 team: Team,
                 attribute: const.CharacterAttribute,
                 state: const.CharacterState):
        self.speed: float = attribute.speed
        self.ability_cd: float = attribute.ability_cd
        self.ability_variables = attribute.ability_variables
        self.move_direction: pg.Vector2 = pg.Vector2(0, 0)
        self.abilities_time: float = -attribute.ability_cd
        self.attack_time: float = -(1/attribute.attack_speed)
        super().__init__(position, attribute, team, state)
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.take_damage, self.__id)
        ev_manager.register_listener(EventEveryTick, self.tick_move)

    def move(self, direction: pg.Vector2):
        """
        Move the character in the given direction.
        """
        original_pos = self.__position

        if direction.length() > self.speed:
            direction = self.speed * direction.normalize()

        game_map = get_model().map

        dirs = [pg.Vector2(direction.x, 0), pg.Vector2(0, direction.y)]

        for dir in dirs:
            # set the minimum move into 1/4 of the original direction
            min_direction = dir / 4
            cur_direction = dir / 4

            # try further distance
            for i in range(4):

                new_position = self.__position + cur_direction
                new_position.x = util.clamp(new_position.x, 0, const.ARENA_SIZE[0] - 1)
                new_position.y = util.clamp(new_position.y, 0, const.ARENA_SIZE[1] - 1)

                if game_map.get_type(new_position) == const.map.MAP_OBSTACLE:
                    self.__position = new_position - min_direction
                    break

                if i == 3:
                    self.__position = new_position

                cur_direction += min_direction

        get_event_manager().post(EventCharacterMove(character=self, original_pos=original_pos))

    def tick_move(self, _: EventEveryTick):
        """Move but it is called by every tick."""
        self.move(self.move_direction)

    def take_damage(self, event: EventAttack):
        self.health -= event.attacker.attack_damage
        if self.health <= 0:
            self.die()

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        dist = self.__position.distance_to(enemy.position)
        if self.__team != enemy.team and dist <= self.__attack_range and (now_time - self.attack_time) * self.__attack_speed >= 1:
            get_event_manager().post(EventAttack(attacker=self, victim=enemy), enemy.id)
            self.attack_time = now_time

    def die(self):
        print(f"Character {self.__id} in Team {self.__team.id} died")
        self.alive = False
        # self.__hidden = True
        super().discard()
        get_event_manager().post(EventCharacterDied(character=self))

    def cast_ability(self, *args, **kwargs):
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.ability_cd:
            return
        print("cast abilities")
        self.abilities_time = now_time
        self.ability(*args, **kwargs)

    def ability(self, *args, **kwargs):
        pass
