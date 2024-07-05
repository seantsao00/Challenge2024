"""
The module defines Entity class.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

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

    def __init__(self, position: pg.Vector2 | tuple[float, float],
                 entity_type: str = 'default', team: Team = None, imgstate: str = 'default'):
        Entity.entity_id += 1
        self.id: int = Entity.entity_id
        self.position: pg.Vector2 = pg.Vector2(position)
        self.type: str = entity_type
        self.imgstate: str = imgstate
        self.hidden: bool = False
        self.team: Team = team
        get_event_manager().post(EventCreateEntity(entity=self))

    def discard(self):
        ev_manager = get_event_manager()
        ev_manager.post(EventDiscardEntity, self.id)


class LivingEntity(Entity):
    def __init__(self, health: float, position: pg.Vector2 | tuple[float, float], vision: float,
                 entity_type: str = 'default', team: Team = None, imgstate: str = 'default') -> None:
        self.alive: bool = True
        self.health: float = health
        self.max_health: float = health
        self.vision: float = vision
        super().__init__(position, entity_type=entity_type, team=team, imgstate=imgstate)
