from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.map
import util
import view
from event_manager import EventAttack, EventCharacterDied, EventCharacterMove
from instances_manager import get_event_manager, get_model
from model.entity import Entity, LivingEntity

if TYPE_CHECKING:
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
        super().__init__(health, position, vision, entity_type='team' + str(team.id), team=team, imgstate=imgstate)
        self.speed: float = speed
        self.attack_range: float = attack_range
        self.damage: float = damage
        self.alive: bool = True
        self.abilities_time: float = -100
        self.abilities_cd: float = abilities_cd
        self.attack_speed: int = attack_speed
        self.attack_time: float = -100
        model = get_model()
        if model.show_view_range:
            self.view.append(view.ViewRangeView(self))
        if model.show_attack_range:
            self.view.append(view.AttackRangeView(self))
        self.view.append(view.AbilitiesCDView(self))
        if self.health is not None:
            self.view.append(view.HealthView(self))
        get_event_manager().register_listener(EventAttack, self.take_damage, self.id)

    def move(self, direction: pg.Vector2):
        """
        Move the character in the given direction.
        """
        original_pos = self.position

        if direction.length() > self.speed:
            direction = self.speed * direction.normalize()

        game_map = get_model().map

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
                get_event_manager().post(EventCharacterMove(character=self, original_pos=original_pos))
                return

            if game_map.get_type(new_position) == const.map.MAP_OBSTACLE:
                self.position = new_position - min_direction
                get_event_manager().post(EventCharacterMove(character=self, original_pos=original_pos))
                return

            if i == 3:
                self.position = new_position
                get_event_manager().post(EventCharacterMove(character=self, original_pos=original_pos))
                return

            cur_direction += min_direction

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
        if self in get_model().characters:
            get_model().characters.remove(self)
            get_event_manager().post(EventCharacterDied(character=self))
        self.alive = False
        self.hidden = True

    def call_abilities(self, *args):
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.abilities_cd:
            print('can not use abilities')
            return
        self.abilities_time = now_time
        self.abilities(*args)

    def abilities(self):
        return
