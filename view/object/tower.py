import pygame as pg

import model.tower
from view.object.entity import Entity
import model


class Tower(Entity):
    def __init__(self, tower: model.tower):
        super().__init__()
        self.tower = tower
