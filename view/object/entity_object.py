from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from event_manager import EventDiscardEntity
from instances_manager import get_event_manager
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import Entity


class EntityObject(ObjectBase):

    def __init__(self, canvas: pg.Surface, entity: Entity):
        self.entity: Entity = entity
        self.position: pg.Vector2 = self.entity.position.copy()
        super().__init__(canvas, self.position[1])
        self.register_listeners()

    def handle_discard_entity(self, _: EventDiscardEntity):
        self.exist = False
        ev_manager = get_event_manager()
        ev_manager.unregister_listener(
            EventDiscardEntity, self.handle_discard_entity, self.entity.id)

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(
            EventDiscardEntity, self.handle_discard_entity, self.entity.id)