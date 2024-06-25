import pygame as pg

import model
import model.tower
from view.object.entity import Entity


class Tower(Entity):
    def __init__(self, tower: model.tower):
        super().__init__()
        self.tower = tower
