import pygame as pg

import const


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
        - canvas: the Surface object blited.
        - ratio: the ratio between model's coordinate and the canvas size.
        - render_position: the position the image should be rendered.
        - height: Determines the rendering order of the image on the screen.
            A Lower value indicates the image is rendered earlier, and thus placed on a rearer layer.
        """
        cls.image_initialized = True

    def __init__(self, canvas: pg.Surface, ratio: float, height: float = const.WINDOW_SIZE[1]):
        self.canvas: pg.Surface = canvas
        self.ratio: float = ratio
        self.height: float = height
        if not self.image_initialized:
            self.init_convert()

    def draw(self):
        """
        Draw the object to the screen
        """

    def update(self):
        """
        update the position and the height of the object
        """
