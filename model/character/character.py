from __future__ import annotations

from enum import Enum, auto
from threading import Lock
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


class CharacterMovingState(Enum):
    STOPPED = auto()
    TO_POSITION = auto()
    TO_DIRECTION = auto()


class CharacterAttackResult(Enum):
    SUCCESS = auto()
    OUT_OF_RANGE = auto()
    COOLDOWN = auto()
    FRIENDLY_FIRE = auto()

    def __bool__(self):
        return self == self.SUCCESS


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
     - __move_state: How is the character moving currently.
     - __move_path: The path to reach the target position
       (useful when __move_state == TO_LOCATION).
     - __move_direction: The direction the character is facing and moving toward
       (useful when __move_state == TO_DIRECTION).
    """

    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 team: Team,
                 attribute: const.CharacterAttribute,
                 entity_type: const.CharacterType,
                 state: const.CharacterState):
        self.abilities_time: float = -attribute.ability_cd
        self.__attack_time: float = -1 / attribute.attack_speed
        self.moving_lock = Lock()
        self.__move_state: CharacterMovingState = CharacterMovingState.STOPPED
        self.__move_path: list[pg.Vector2] = []
        self.__move_direction: pg.Vector2 = pg.Vector2(0, 0)

        super().__init__(position, attribute, team, entity_type, state)

        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.take_damage, self.id)
        ev_manager.register_listener(EventEveryTick, self.tick_move)

        self.attribute: const.CharacterAttribute

    def __move_toward_direction(self):
        """
        Move the character in the given direction.
        """
        direction = self.__move_direction
        original_pos = self.position

        model = get_model()
        if direction.length() > 0:
            direction = self.attribute.speed * model.dt * direction.normalize()

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

                if not game_map.is_position_passable(new_position):
                    self.position = new_position - min_direction
                    break

                if i == 3:
                    self.position = new_position

                cur_direction += min_direction

        get_event_manager().post(EventCharacterMove(character=self, original_pos=original_pos))

    def __move_toward_position(self):
        """
        move along the predetermined path as far as it can
        """
        esp = 1e-8

        if len(self.__move_path) == 0:
            return

        it = 0
        pos_init = self.position
        movement = 0
        model = get_model()
        while (it < len(self.__move_path)
               and movement + esp <= self.attribute.speed * model.dt):
            ratio = ((self.attribute.speed * model.dt - movement)
                     / (self.__move_path[it] - self.position).length())
            if ratio >= 1:
                movement += (self.__move_path[it] - self.position).length()
                self.position = self.__move_path[it]
                it += 1
            else:
                self.position = self.__move_path[it] * ratio + self.position * (1 - ratio)
                break

        if it == len(self.__move_path):
            self.__move_path = []
            self.__move_state = CharacterMovingState.STOPPED
            print(f"[API] Character {self.id}: arrive at destination")
        else:
            del self.__move_path[:it]

        get_event_manager().post(EventCharacterMove(character=self, original_pos=pos_init))

    def tick_move(self, _: EventEveryTick):
        """Move but it is called by every tick."""
        with self.moving_lock:
            if self.__move_state == CharacterMovingState.TO_DIRECTION:
                self.__move_toward_direction()
            elif self.__move_state == CharacterMovingState.TO_POSITION:
                self.__move_toward_position()

    def set_move_stop(self) -> bool:
        """Stop movement of the character. Returns True/False on success/failure."""
        self.__move_state = CharacterMovingState.STOPPED
        return True

    def set_move_direction(self, direction: pg.Vector2):
        """Set character movement toward a direction. Returns True/False on success/failure."""
        self.__move_state = CharacterMovingState.TO_DIRECTION
        self.__move_direction = direction
        return True

    def set_move_position(self, path: list[pg.Vector2]):
        """Set character movement toward a target position. Returns True/False on success/failure."""
        if path is None:
            return False
        self.__move_path = path
        self.__move_state = CharacterMovingState.TO_POSITION
        return True

    def take_damage(self, event: EventAttack):
        self.health -= event.attacker.attribute.attack_damage
        if self.health <= 0:
            self.die()

    def attackable(self, enemy: Entity) -> CharacterAttackResult:
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if self.team == enemy.team:
            return CharacterAttackResult.FRIENDLY_FIRE
        elif dist > self.attribute.attack_range:
            return CharacterAttackResult.OUT_OF_RANGE
        elif (now_time - self.__attack_time) * self.attribute.attack_speed < 1:
            return CharacterAttackResult.COOLDOWN
        else:
            return CharacterAttackResult.SUCCESS

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        if self.attackable(enemy):
            get_event_manager().post(EventAttack(attacker=self, victim=enemy), enemy.id)
            self.__attack_time = now_time

    def die(self):
        print(f"Character {self.id} in Team {self.team.team_id} died")
        self.alive = False
        # self.hidden = True
        get_event_manager().post(EventCharacterDied(character=self))
        get_event_manager().unregister_listener(EventEveryTick, self.tick_move)
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
