import pygame as pg

from view.object.object_base import ObjectBase
import const
import model


class TestObject(ObjectBase):
    """
    
    """

    def __init__(self, object,
                 size: float=const.TEST_OBJECT_DEFAULT_SIZE, color=const.TEST_OBJECT_DEFAULT_COLOR):
        if not hasattr(object, 'position'):
            raise AttributeError('object must have attribute position.')
        super().__init__()
        self.position = object
        self.size = size
        self.color = color

    def draw(self, screen: pg.Surface):
        pg.draw.circle(screen, const.TEST_OBJECT_DEFAULT_COLOR, self.position, self.size)
