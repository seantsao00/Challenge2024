import pygame as pg

import model.fountain
from view.object.entity import Entity
import model


class Tower(Entity):
    def __init__(self, spring: model.fountain):
        super().__init__()
        self.tower = spring
