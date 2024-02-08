import pygame as pg


class ObjectBase:
    """
    The superclass of all graphical objects that require loading images.

    This class serve as an interface defining the basic framework for graphical objects.
    """
    image_initialized = False
    images: tuple | dict = tuple()

    @classmethod
    def init_convert(cls):
        """
        Load images into self.images.
    
        To avoid loading the same image multiple times,
        once first instance is created and init_convert is called,
        image_initialized within the class will be set to True.
        """
        cls.image_initialized = True

    def __init__(self):
        if not self.image_initialized:
            self.init_convert()

    def draw(self, screen: pg.Surface):
        """
        Draw the object to the screen
        """
