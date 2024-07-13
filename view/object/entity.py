from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from model import Bullet
from util import crop_image
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Entity


class EntityView(EntityObject):
    __images: dict[tuple[const.PartyType, const.EntityType, const.EntityState],
                   pg.Surface] = {}
    """
    structure: images[party][entity][state]

    The static dict that stores entity images.

    This dict is shared among all Entity instances,
    built from const, and initialized only once in init_convert.
    """

    def __init__(self, canvas: pg.Surface, entity: Entity):
        self.entity: Entity = entity
        super().__init__(canvas, entity, self.entity.position[1])
        self.register_listeners()

    @classmethod
    def init_convert(cls):
        for party, entity_dict in const.ENTITY_IMAGE.items():
            for entity, state_dict in entity_dict.items():
                for state, path in state_dict.items():
                    img = pg.image.load(path)
                    w = const.ENTITY_SIZE[entity][state] * 2 * ScreenInfo.resize_ratio
                    h = const.ENTITY_SIZE[entity][state] * 2 * ScreenInfo.resize_ratio
                    cls.__images[(party, entity, state)] = crop_image(img, w, h).convert_alpha()
        cls.image_initialized = True

    def draw(self):
        entity = self.entity
        img = self.__images[(entity.team.party, entity.entity_type, entity.state)]
        if isinstance(self.entity, Bullet):
            img = pg.transform.rotate(img, self.entity.view_rotate)
        self.canvas.blit(img, img.get_rect(center=ScreenInfo.resize_ratio *
                         (entity.position + const.DRAW_DISPLACEMENT)))

    def update(self):
        if not self.exist:
            return False
        self.priority[1] = int(self.entity.position[1])
        self.priority[2] = int(self.entity.position[0])
        return True
