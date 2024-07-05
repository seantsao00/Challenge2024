from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import util
import view
from event_manager import EventAttack, EventCharacterDied, EventCharacterMove, EventEveryTick
from instances_manager import get_event_manager, get_model
from model.entity import Entity, LivingEntity

if TYPE_CHECKING:
    from model.building import Linked_list, Node
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

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team, speed: float,
                 attack_range: float, damage: float, health: float, vision: float, attack_speed: float, abilities_cd: float, imgstate: str):
        super().__init__(health, position, vision, entity_type=team.name, team=team, imgstate=imgstate)
        self.speed: float = speed
        self.attack_range: float = attack_range
        self.damage: float = damage
        self.abilities_time: float = -100
        self.abilities_cd: float = abilities_cd
        self.attack_speed: int = attack_speed
        self.attack_time: float = -100
        self.move_direction: pg.Vector2 = pg.Vector2(0, 0)
        model = get_model()
        if model.show_view_range:
            self.view.append(view.ViewRangeView(self))
        if model.show_attack_range:
            self.view.append(view.AttackRangeView(self))
        self.view.append(view.AbilitiesCDView(self))
        if self.health is not None:
            self.view.append(view.HealthView(self))
        get_event_manager().register_listener(EventAttack, self.take_damage, self.id)
        get_event_manager().register_listener(EventEveryTick, self.tick_move)

    def move(self, direction: pg.Vector2):
        """
        Move the character in the given direction.
        """
        original_pos = self.position

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

    def tick_move(self, event: EventEveryTick):
        """Move but it is called by every tick."""
        self.move(self.move_direction)

    def take_damage(self, event: EventAttack):
        self.health -= event.attacker.damage
        if self.health <= 0:
            self.die()

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if self.team != enemy.team and dist <= self.attack_range and (now_time - self.attack_time) * self.attack_speed >= 1:
            get_event_manager().post(EventAttack(attacker=self, victim=enemy), enemy.id)
            self.attack_time = now_time

    def die(self):
        print(f"Character {self.id} in Team {self.team.id} died")
        self.alive = False
        self.hidden = True
        get_event_manager().post(EventCharacterDied(character=self))

    def call_abilities(self, *args, **kwargs):
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.abilities_cd:
            return
        self.abilities_time = now_time
        self.abilities(*args, **kwargs)

    def abilities(self, *args, **kwargs):
        pass
