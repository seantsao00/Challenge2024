from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

import pygame as pg

import const
from util import crop_image
from view.object.entity_object import EntityObject
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Entity


class EntityView(EntityObject):
    images: dict[const.PartyType, dict[const.EntityType, dict[const.EntityState, pg.Surface]]] \
        = {party: {
            entity_type: {} for entity_type in chain(const.CharacterType, const.TowerType, const.BulletType)
        } for party in const.PartyType}
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
                    width = const.ENTITY_SIZE[entity][state] * 2 * ScreenInfo.resize_ratio
                    height = const.ENTITY_SIZE[entity][state] * 2 * ScreenInfo.resize_ratio
                    cls.images[party][entity][state] = crop_image(
                        img, width, height
                    ).convert_alpha()
        cls.image_initialized = True

    def draw(self):
        entity = self.entity
        img = self.images[entity.team.party][entity.entity_type][entity.state]
        self.canvas.blit(img, img.get_rect(center=ScreenInfo.resize_ratio *
                         (entity.position + const.DRAW_DISPLACEMENT)))

    def update(self):
        if not self.exist:
            return False
        self.priority[1] = int(self.entity.position[1])
        self.priority[2] = int(self.entity.position[0])
        return True
