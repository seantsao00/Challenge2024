"""
The module defines Entity class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager.events import EventCreateEntity, EventDiscardEntity
from instances_manager import get_event_manager
from util import log_info

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

    __entity_id: int = 0

    def __init__(self,
                 position: pg.Vector2 | tuple[float, float],
                 team: Team,
                 entity_type: const.EntityType,
                 state: const.EntityState = None):
        Entity.__entity_id += 1
        self.__id: int = Entity.__entity_id
        self.position: pg.Vector2 = pg.Vector2(position)
        self.team: Team = team
        self.__entity_type: const.EntityType = entity_type
        self.state: const.EntityState = state
        get_event_manager().post(EventCreateEntity(entity=self))

    def __str__(self):
        return f'living entity {self.id} (team {self.team.team_id})'

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
                 state: const.EntityState = None,
                 invulnerability: bool = False):
        self.alive: bool = True
        self.attribute: const.LivingEntityAttribute = attribute
        self.health: float = self.attribute.max_health

        self.__invulnerability: bool = invulnerability

        super().__init__(position, team, entity_type, state)

    def vulnerable(self, enemy: Entity):
        """
        Test vulnerability. `Enemy` is only used for logging.
        """
        if self.__invulnerability:
            log_info(f"[Attack] {self} is invulnerable, {enemy}'s attack failed")
            return False
        if not self.alive:
            log_info(f"[Attack] {self} is already dead, {enemy}'s attack failed")
            return False
        return True
