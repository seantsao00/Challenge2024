from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame as pg

import const
import util
from event_manager import EventAttack, EventCreateEntity, EventDiscardEntity, EventEveryTick
from instances_manager import get_event_manager, get_model
from model.character import Character
from model.entity import Entity

if TYPE_CHECKING:
    from model.team import Team


class Vehicle(Entity):
    """
    Class for vehicle character in the game.
    This character is not generated every map.
    """
    __rng = random.Random()

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team, state: const.VehicleState):
        super().__init__(position, team,
                         Vehicle.__rng.choices(list(const.VehicleType),
                                               [const.VEHICLE_RARITY[color] for color in list(const.VehicleType)], k=1)[0],
                         state)
        if state is const.VehicleState.BACK:
            self.direction = pg.Vector2(0, -const.VEHICLE_SPEED)
        elif state is const.VehicleState.FRONT:
            self.direction = pg.Vector2(0, const.VEHICLE_SPEED)
        elif state is const.VehicleState.LEFT:
            self.direction = pg.Vector2(-const.VEHICLE_SPEED, 0)
        elif state is const.VehicleState.RIGHT:
            self.direction = pg.Vector2(const.VEHICLE_SPEED, 0)
        else:
            raise ValueError

    def tick_move(self, dt) -> tuple[float, float, float, float]:
        move = self.direction * dt
        if self.entity_type is const.VehicleType.SCOOTER:
            if self.direction.x > 0:
                self.state = const.VehicleState.SCOOTER_RIGHT
            else:
                self.state = const.VehicleState.SCOOTER_LEFT
        if self.entity_type == const.VehicleType.SCOOTER:
            self.direction.rotate_ip(self.__rng.uniform(-5, 7))
        left = self.direction.normalize() * const.VEHICLE_WIDTH
        # Orthogonal vector
        left.x, left.y = left.y, -left.x
        right = -left
        xs = [0, move.x, left.x, right.x]
        ys = [0, move.y, left.y, right.y]
        max_x = self.position.x + max(xs)
        min_x = self.position.x + min(xs)
        max_y = self.position.y + max(ys)
        min_y = self.position.y + min(ys)
        self.position += move
        return (min_x, max_x, min_y, max_y)

    def check_out_of_bounds(self):
        W = const.ARENA_SIZE[1]
        if self.position.x < 0 or self.position.x > W or self.position.y < 0 or self.position.y > W:
            self.discard()
            return True
        return False


class VehicleManager:
    """Manager for all vehicles. This is used to manage and unify all vehicle. In order to reduce attack check time."""

    def __init__(self):
        self.vehicle_list: list[Vehicle] = []
        get_event_manager().register_listener(EventCreateEntity, self.append_vehicle)
        get_event_manager().register_listener(EventEveryTick, self.every_tick)

    def append_vehicle(self, event: EventCreateEntity):
        if isinstance(event.entity, Vehicle):
            self.vehicle_list.append(event.entity)

    def every_tick(self, event: EventEveryTick):
        # Do a simple sweep line. Otherwise that might be too slow for O(cars * entities)
        dt = get_model().dt
        boxes = [car.tick_move(dt) for car in self.vehicle_list]
        queries = ([(x, +1, ly, ry) for x, _, ly, ry in boxes] +
                   [(x + 1, -1, ly, ry) for _, x, ly, ry in boxes])
        with get_model().entity_lock:
            queries += [(e.position.x, 0, e.position.y, e)
                        for e in get_model().entities.values() if isinstance(e, Character)]
        queries.sort(key=lambda x: (x[0], abs(x[1])))
        Y = const.ARENA_SIZE[1]
        counter = [0] * Y
        hit = []
        for x, m, a, b in queries:
            if m == 0:
                # query a entities is hit
                y = int(util.clamp(a, 0, Y - 1))
                entity = b
                if counter[y] > 0:
                    hit.append(entity)
            else:
                ly, ry = int(util.clamp(a, 0, Y - 1)), int(util.clamp(b, 0, Y - 1))
                for i in range(ly, ry + 1):
                    counter[i] += m
        ev_man = get_event_manager()
        # Take anyone as scapegoat: It doesn't matter
        for entity in hit:
            ev_man.post(EventAttack(
                attacker=self.vehicle_list[0], victim=entity, damage=const.VEHICLE_DAMAGE), entity.id)

        self.vehicle_list = [
            vehicle for vehicle in self.vehicle_list if not vehicle.check_out_of_bounds()]
