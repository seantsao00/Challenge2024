from __future__ import annotations

from typing import Iterable

import pygame as pg


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
    """the ratio between model's coordinate and the canvas size."""

    @classmethod
    def init_convert(cls):
        """
        Load images into self.images.

        To avoid loading the same image multiple times,
        once first instance is created and init_convert is called,
        image_initialized within the class will be set to True.

        """
        cls.image_initialized = True

    def __init__(self, canvas: pg.Surface, priority: Iterable[float]):
        self.canvas: pg.Surface = canvas
        self.priority: Iterable[float] = priority
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
