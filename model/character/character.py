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
                 entity_type: const.CharacterType,
                 state: const.CharacterState):
        self.move_direction: pg.Vector2 = pg.Vector2(0, 0)
        self.abilities_time: float = -attribute.ability_cd
        self.__attack_time: float = -1 / attribute.attack_speed

        super().__init__(position, attribute, team, entity_type, state)

        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.take_damage, self.id)
        ev_manager.register_listener(EventEveryTick, self.tick_move)

        self.attribute: const.CharacterAttribute

    def move(self, direction: pg.Vector2):
        """
        Move the character in the given direction.
        """
        original_pos = self.position

        if direction.length() > self.attribute.speed:
            direction = self.attribute.speed * direction.normalize()

        game_map = get_model().map

        component_dirs = [pg.Vector2(direction.x, 0), pg.Vector2(0, direction.y)]

        for component_dir in component_dirs:
            # set the minimum move into 1/4 of the original direction
            min_direction = component_dir / 4
            cur_direction = component_dir / 4

            # try further distance
            for i in range(4):

                new_position = self.position + cur_direction
                new_position.x = util.clamp(new_position.x, 0, const.ARENA_SIZE[0] - 1)
                new_position.y = util.clamp(new_position.y, 0, const.ARENA_SIZE[1] - 1)

                if game_map.get_type(new_position) == const.map.MAP_OBSTACLE:
                    self.position = new_position - min_direction
                    break

                if i == 3:
                    self.position = new_position

                cur_direction += min_direction

        get_event_manager().post(EventCharacterMove(character=self, original_pos=original_pos))

    def tick_move(self, _: EventEveryTick):
        """Move but it is called by every tick."""
        self.move(self.move_direction)

    def take_damage(self, event: EventAttack):
        self.health -= event.attacker.attribute.attack_damage
        if self.health <= 0:
            self.die()

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team
            and dist <= self.attribute.attack_range
                and (now_time - self.__attack_time) * self.attribute.attack_speed >= 1):
            get_event_manager().post(EventAttack(attacker=self, victim=enemy), enemy.id)
            self.__attack_time = now_time

    def die(self):
        print(f"Character {self.id} in Team {self.team.team_id} died")
        self.alive = False
        # self.hidden = True
        get_event_manager().post(EventCharacterDied(character=self))
        super().discard()

    def cast_ability(self, *args, **kwargs):
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.attribute.ability_cd:
            return
        print("cast abilities")
        self.abilities_time = now_time
        self.ability(*args, **kwargs)

    def ability(self, *args, **kwargs):
        pass
