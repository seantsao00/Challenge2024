"""
The module defines Entity class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager.events import EventCreateEntity, EventDiscardEntity
from instances_manager import get_event_manager

if TYPE_CHECKING:
    from model.team import Team


class Entity:
    """
    Class for entity (object) in the game, including NPCs.
    Each entity has the following property:
     - `id`: unique ID for each entity.
     - `position`: initial position 
     - type: entity type, used for determine the image type
     - imgstate: used for different image for the same type
     - hidden: the entity will not render if it is True.
     - team: the owner team of this entity.
    """

    entity_id: int = 0

    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 team: Team,
                 entity_type: const.EntityType,
                 state: const.EntityState = None):
        Entity.entity_id += 1
        self.__id: int = Entity.entity_id
        self.__position: pg.Vector2 = pg.Vector2(position)
        self.__team: Team = team
        self.__entity_type: const.EntityType = entity_type
        self.__state: const.EntityState = state
        self.__hidden: bool = False
        get_event_manager().post(EventCreateEntity(entity=self))

    def discard(self):
        ev_manager = get_event_manager()
        ev_manager.post(EventDiscardEntity, self.__id)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def position(self) -> pg.Vector2:
        return self.__position

    @property
    def team(self) -> Team:
        return self.__team

    @property
    def entity_type(self) -> const.EntityType:
        return self.__entity_type

    @property
    def state(self) -> const.EntityState:
        return self.__state

    @property
    def hidden(self) -> bool:
        return self.__hidden


class LivingEntity(Entity):
    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 attribute: const.LivingEntityAttribute,
                 team: Team,
                 entity_type: const.EntityType,
                 state: const.EntityState = None):
        self.__alive: bool = True
        self.__vision: float = attribute.vision
        self.__max_health: float = attribute.max_health
        self.__attack_damage: float = attribute.attack_damage
        self.__attack_speed: float = attribute.attack_speed
        self.__attack_range: float = attribute.attack_range

        self.__health: float = self.__max_health
        super().__init__(position, team, entity_type, state)

    @property
    def alive(self) -> bool:
        return self.__alive

    @property
    def max_health(self) -> float:
        return self.__max_health

    @property
    def vision(self) -> float:
        return self.__vision

    @property
    def health(self) -> float:
        return self.__health

    @property
    def attack_damage(self) -> float:
        return self.__attack_damage

    @property
    def attack_speed(self) -> float:
        return self.__attack_speed

    @property
    def attack_range(self) -> float:
        return self.__attack_range
