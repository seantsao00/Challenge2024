from __future__ import annotations

from abc import abstractmethod
from enum import Enum, auto
from random import uniform
from threading import Lock
from typing import TYPE_CHECKING

import pygame as pg

import const
import util
from event_manager import EventAttack, EventCharacterDied, EventCharacterMove, EventEveryTick
from instances_manager import get_event_manager, get_model
from model.entity import LivingEntity
from model.path_finder import PathFinder
from util import log_info

if TYPE_CHECKING:
    from model.entity import Entity
    from model.team import Team


class CharacterMovingState(Enum):
    STOPPED = auto()
    TO_POSITION = auto()
    TO_DIRECTION = auto()
    WANDERING = auto()


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
     - __is_wandering: If the character is wandering. Wandering is only used by api methods.
    """

    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 team: Team,
                 attribute: const.CharacterAttribute,
                 entity_type: const.CharacterType,
                 state: const.CharacterState):
        self.abilities_time: float = -attribute.ability_cd
        self._last_attack_time: float = -1 / attribute.attack_speed
        self.moving_lock = Lock()
        self.__move_state: CharacterMovingState = CharacterMovingState.STOPPED
        self.__move_path: list[pg.Vector2] = []
        self.__move_direction: pg.Vector2 = pg.Vector2(0, 0)

        super().__init__(position, attribute, team, entity_type, state)

        ev_manager = get_event_manager()
        ev_manager.register_listener(EventAttack, self.take_damage, self.id)
        ev_manager.register_listener(EventEveryTick, self.tick_move)

        self.attribute: const.CharacterAttribute

    def __str__(self):
        return f'character {self.id} (team {self.team.team_id})'

    def __move_along_direction(self):
        """
        Move the character in the given direction.
        """
        direction = self.__move_direction
        original_pos = self.position

        model = get_model()
        if direction.length() > 0:
            direction = self.get_speed() * model.dt * direction.normalize()

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

                if not model.map.is_position_passable(new_position):
                    self.position = new_position - min_direction
                    break

                if i == 3:
                    self.position = new_position

                cur_direction += min_direction

        self.update_face_direction(self.__move_direction)
        get_event_manager().post(EventCharacterMove(character=self, original_pos=original_pos))

    def __move_along_path(self) -> bool:
        """
        move along the predetermined path as far as it can.
        returns whether the character has arrived
        """
        eps = 1e-8

        if self.__move_path is None or len(self.__move_path) == 0:
            return True

        it = 0
        pos_init = self.position
        movement = 0
        model = get_model()
        while (it < len(self.__move_path)
               and movement + eps <= self.get_speed() * model.dt):
            if (self.__move_path[it] - self.position).length() < eps:
                it += 1
                continue
            ratio = ((self.get_speed() * model.dt - movement)
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
            return True
        else:
            del self.__move_path[:it]

        self.update_face_direction(self.position - pos_init)
        get_event_manager().post(EventCharacterMove(character=self, original_pos=pos_init))
        return False

    def __set_wander_destination(self, path_finder: PathFinder | None) -> bool:
        """
        path_finder is the path finder to use. None means it's on the main thread,
        so model.path_finder will be used
        """
        destination = pg.Vector2([uniform(0, const.ARENA_SIZE[0]),
                                 uniform(0, const.ARENA_SIZE[1])])
        cnt = 0
        while (self.team.vision.position_inside_vision(destination) or get_model().map.get_position_type(destination) is const.MAP_OBSTACLE) and cnt < const.MAX_WANDERING:
            destination = pg.Vector2([uniform(0, const.ARENA_SIZE[0]),
                                     uniform(0, const.ARENA_SIZE[1])])
            cnt += 1
        if cnt >= const.MAX_WANDERING:
            return False
        if path_finder is None:
            path_finder = get_model().path_finder
        self.__move_path = path_finder.find_path(self.position, destination)
        if self.__move_path is None:
            return False
        return True

    def tick_move(self, _: EventEveryTick):
        """Move but it is called by every tick."""
        with self.moving_lock:
            if self.__move_state == CharacterMovingState.TO_DIRECTION:
                self.__move_along_direction()
            elif self.__move_state == CharacterMovingState.TO_POSITION:
                arrived = self.__move_along_path()
                if arrived:
                    self.__move_state = CharacterMovingState.STOPPED
                    log_info(f"[API] Character {self.id}: arrive at destination")
            elif self.__move_state == CharacterMovingState.WANDERING:
                arrived = self.__move_along_path()
                if arrived:
                    self.__set_wander_destination(None)

    def set_move_stop(self) -> bool:
        """Stop movement of the character. Returns True/False on success/failure."""
        self.__move_state = CharacterMovingState.STOPPED
        return True

    def set_move_direction(self, direction: pg.Vector2) -> bool:
        """Set character movement toward a direction. Returns True/False on success/failure."""
        self.__move_state = CharacterMovingState.TO_DIRECTION
        self.__move_direction = direction
        return True

    def set_move_position(self, path: list[pg.Vector2] | None):
        """Set character movement toward a target position. Returns True/False on success/failure."""
        if path is None:
            return False
        self.__move_path = path
        self.__move_state = CharacterMovingState.TO_POSITION
        self.__move_direction = pg.Vector2(0, 0)
        return True

    def set_wandering(self, path_finder: PathFinder) -> bool:
        """Set the character to be wandering. Returns True/False on success/failure. If the character is already wandering, this method will return False. """
        if self.__move_state == CharacterMovingState.WANDERING:
            return False
        if not self.__set_wander_destination(path_finder):
            return False
        self.__move_state = CharacterMovingState.WANDERING
        return True

    def take_damage(self, event: EventAttack):
        if not self.vulnerable(event.attacker):
            return

        self.health -= event.damage
        if self.health <= 0:
            self.die()
            if event.attacker.team.party is not const.PartyType.NEUTRAL:
                event.attacker.team.gain_point_kill()
                log_info(
                    f"[Team] {event.attacker.team.team_name} get score, score is {event.attacker.team.points}")

    def reachable(self, position: pg.Vector2):
        """
        Test whether some position is within my reach range.
        This method is used by attack and ranger ability cast.
        """
        dist = self.position.distance_to(position)
        return dist <= self.attribute.attack_range

    def attackable(self, enemy: LivingEntity):
        """Test whether cooldown is ready and enemy is within range. If ready then reset it."""
        now_time = get_model().get_time()
        if not self.reachable(enemy.position):
            log_info(f"[Attack] {self} is attacking an enemy {enemy} out of range")
            return False
        if self.team is enemy.team:
            log_info(f"[Attack] {self} is attacking an enemy {enemy} within the same team")
            return False
        if (now_time - self._last_attack_time) * self.attribute.attack_speed < 1:
            log_info(f"[Attack] {self} is attacking too fast!")
            return False
        self._last_attack_time = now_time
        return True

    def update_face_direction(self, direction: pg.Vector2 | None):
        if direction == None or direction == pg.Vector2(0, 0):
            return
        if direction.x <= 0:
            self.state = const.CharacterState.LEFT
        else:
            self.state = const.CharacterState.RIGHT

    @abstractmethod
    def attack(self, enemy: Entity):
        pass

    def die(self):
        log_info(f"Character {self.id} in Team {self.team.team_id} died")
        self.alive = False
        # self.hidden = True
        get_event_manager().post(EventCharacterDied(character=self))
        get_event_manager().unregister_listener(EventEveryTick, self.tick_move)
        super().discard()

    def get_speed(self):
        return self.attribute.speed * (const.PUDDLE_SPEED_RATIO if get_model().map.is_position_puddle(self.position) else 1)

    @abstractmethod
    def cast_ability(self, *args, **kwargs):
        pass

    @abstractmethod
    def manual_cast_ability(self, *args, **kwargs):
        """
        This is a (somewhat bad) workaround for manual ability casting, 
        because I did not come up a nice solution to integrate with API.
        Refactor will be great.
        """

    @property
    def move_direction(self) -> pg.Vector2:
        return self.__move_direction

    @property
    def move_path(self) -> list[pg.Vector2] | None:
        return self.__move_path

    @property
    def move_destination(self) -> pg.Vector2 | None:
        if self.__move_state == CharacterMovingState.TO_POSITION or self.__move_state == CharacterMovingState.WANDERING:
            if self.__move_path != None and len(self.__move_path) > 0:
                return self.__move_path[-1]
            return self.position
        return None

    @property
    def move_state(self) -> CharacterMovingState:
        return self.__move_state

    @property
    def is_wandering(self) -> bool:
        return self.__move_state == CharacterMovingState.WANDERING
