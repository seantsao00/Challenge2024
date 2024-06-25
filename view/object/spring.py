import pygame as pg

import model
import model.fountain
from view.object.entity import Entity


class Tower(Entity):
    def __init__(self, spring: model.fountain):
        super().__init__()
        self.tower = spring
