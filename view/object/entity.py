import pygame as pg

import const
import model
from util import crop_image
from view.object.object_base import ObjectBase


class EntityView(ObjectBase):
    images: dict[str, dict[str, pg.Surface]] = {}
    """
    The static dict that stores entity images.

    This dict is shared among all Entity instances,
    built from const, and initialized only once in init_convert.
    """

    def __init__(self, entity: 'model.Entity'):
        super().__init__()
        self.entity = entity
        self.position = self.entity.position.copy()

    @classmethod
    def init_convert(cls):
        for type, states in const.ENTITY_STATES.items():
            if type not in cls.images:
                cls.images[type] = {}
            for state in states:
                path = (
                    const.IMAGE_PATH +
                    const.ENTITY_IMAGE_PATH +
                    str(type) + '/' +
                    str(state) + '.png'
                )
                img = pg.image.load(path)
                width = const.ENTITY_RADIUS * 2
                height = const.ENTITY_RADIUS * 2
                cls.images[type][state] = crop_image(
                    img, width, height
                ).convert_alpha()
        cls.image_initialized = True

    def draw(self, screen: pg.Surface):
        entity = self.entity
        if entity.hidden == True:
            return
        img = self.images[entity.type][entity.imgstate]
        screen.blit(img, img.get_rect(center=entity.position))
