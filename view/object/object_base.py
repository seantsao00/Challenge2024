import pygame as pg

import const


class ObjectBase:
    """
    The superclass of all graphical objects that require loading images.

    This class serve as an interface defining the basic framework for graphical objects.

    This class has the following attributes:
    - canvas: the Surface object blited.
    - render_position: the position the image should be rendered.
    - priority: Determines the rendering order of the image on the screen, usually is same as its height.
        A Lower value indicates the image is rendered earlier, and thus placed on a rearer layer.
    """
    image_initialized = False
    images: tuple | dict = tuple()
    resize_ratio: float = 1
    """the ratio between model's coordinate and the canvas size."""

    @classmethod
    def set_resize_ratio(cls, resize_ratio: float):
        cls.resize_ratio = resize_ratio

    @classmethod
    def init_convert(cls):
        """
        Load images into self.images.

        To avoid loading the same image multiple times,
        once first instance is created and init_convert is called,
        image_initialized within the class will be set to True.

        """
        cls.image_initialized = True

    def __init__(self, canvas: pg.Surface, priority: float = const.WINDOW_SIZE[1]+10):
        self.canvas: pg.Surface = canvas
        self.priority: float = priority
        self.exist: bool = True
        """If the object is still exist."""
        if not self.image_initialized:
            self.init_convert()

    def draw(self):
        """
        Draw the object to the screen.
        """

    def update(self) -> bool:
        """
        update the position and the height of the object and return if the object is still exist.
        """
        return self.exist
