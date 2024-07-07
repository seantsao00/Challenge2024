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
        self.position: pg.Vector2 = pg.Vector2(position)
        self.team: Team = team
        self.__entity_type: const.EntityType = entity_type
        self.state: const.EntityState = state
        self.hidden: bool = False
        get_event_manager().post(EventCreateEntity(entity=self))

    def discard(self):
        ev_manager = get_event_manager()
        ev_manager.post(EventDiscardEntity(), self.id)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def entity_type(self) -> const.EntityType:
        return self.__entity_type


class LivingEntity(Entity):
    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 attribute: const.LivingEntityAttribute,
                 team: Team,
                 entity_type: const.EntityType,
                 state: const.EntityState = None):
        self.alive: bool = True
        self.vision: float = attribute.vision
        self.max_health: float = attribute.max_health
        self.attack_damage: float = attribute.attack_damage
        self.attack_speed: float = attribute.attack_speed
        self.attack_range: float = attribute.attack_range

        self.health: float = self.max_health
        super().__init__(position, team, entity_type, state)
