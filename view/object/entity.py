from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
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

    def __init__(self, entity: Entity):
        super().__init__()
        self.entity = entity
        self.position = self.entity.position.copy()

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
                width = const.ENTITY_RADIUS * 2
                height = const.ENTITY_RADIUS * 2
                cls.images[entity_type][state] = crop_image(
                    img, width, height
                ).convert_alpha()
        cls.image_initialized = True

    def draw(self, screen: pg.Surface):
        entity = self.entity
        if entity.hidden:
            return
        img = self.images[entity.type][entity.imgstate]
        screen.blit(img, img.get_rect(center=entity.position))
