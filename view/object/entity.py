from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventDiscardEntity
from instances_manager import get_event_manager
from util import crop_image
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import Entity


class EntityView(ObjectBase):
    images: dict[str, dict[str, pg.Surface]] = {}
    """
    The static dict that stores entity images.

    This dict is shared among all Entity instances,
    built from const, and initialized only once in init_convert.
    """

    def __init__(self, canvas: pg.Surface, entity: Entity):
        self.entity: Entity = entity
        self.position: pg.Vector2 = self.entity.position.copy()
        self.exist = True
        super().__init__(canvas, self.position[1])
        self.register_listeners()

    @classmethod
    def init_convert(cls):
        for entity_type, states in const.ENTITY_STATES.items():
            if entity_type not in cls.images:
                cls.images[entity_type] = {}
            for state in states:
                path = (
                    const.IMAGE_PATH +
                    const.ENTITY_IMAGE_PATH +
                    str(entity_type) + '/' +
                    str(state) + '.png'
                )
                img = pg.image.load(path)
                width = const.ENTITY_RADIUS * 2 * cls.resize_ratio
                height = const.ENTITY_RADIUS * 2 * cls.resize_ratio
                cls.images[entity_type][state] = crop_image(
                    img, width, height
                ).convert_alpha()
        cls.image_initialized = True

    def handle_discard_entity(self):
        self.exist = False

    def draw(self):
        entity = self.entity
        if entity.hidden:
            return
        img = self.images[entity.type][entity.imgstate]
        self.canvas.blit(img, img.get_rect(center=self.resize_ratio*entity.position))

    def update(self):
        if not self.exist:
            return False
        self.priority = self.entity.position[1]
        return True

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        ev_manager.register_listener(
            EventDiscardEntity, self.handle_discard_entity, self.entity.id)
