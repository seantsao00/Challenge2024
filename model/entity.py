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
                 party: const.PartyType,
                 entity_type: const.EntityType,
                 state: const.EntityState = None):
        Entity.entity_id += 1
        self.id: int = Entity.entity_id
        self.position: pg.Vector2 = pg.Vector2(position)
        self.party: const.PartyType = party
        self.entity_type: const.EntityType = entity_type
        self.state: const.EntityState = state
        self.hidden: bool = False
        get_event_manager().post(EventCreateEntity(entity=self))

    def discard(self):
        ev_manager = get_event_manager()
        ev_manager.post(EventDiscardEntity, self.id)


class LivingEntity(Entity):
    def __init__(self,
                 max_health: float,
                 position: pg.Vector2 | tuple[float, float],
                 vision: float,
                 party: const.PartyType,
                 entity_type: const.EntityType,
                 state: const.EntityState = None):
        self.alive: bool = True
        self.health: float = max_health
        self.max_health: float = max_health
        self.vision: float = vision
        super().__init__(position, party, entity_type, state)
