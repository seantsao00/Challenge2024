from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_ENTITIES
from event_manager import EventDiscardEntity
from instances_manager import get_event_manager
from view.object.object_base import ObjectBase

# if TYPE_CHECKING:
#     from view.object.range import ViewRangeView, AttackRangeView

if TYPE_CHECKING:
    from model import Entity


class EntityObject(ObjectBase):
    def __init__(self, canvas: pg.Surface, entity: Entity, priority: float = const.WINDOW_SIZE[1] + 10):
        self.entity: Entity = entity
        self.position: pg.Vector2 = self.entity.position.copy()
        super().__init__(canvas, [PRIORITY_ENTITIES, self.position[1]])
        self.register_listeners()

    def handle_discard_entity(self, _: EventDiscardEntity):
        self.exist = False

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(
            EventDiscardEntity, self.handle_discard_entity, self.entity.id)

    def unregister_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.unregister_listener(EventDiscardEntity, self.handle_discard_entity,
                                       self.entity.id)
