import pygame as pg

import model
import model.building.fountain
from view.object.entity import Entity


class Tower(Entity):
    def __init__(self, spring: model.building.fountain):
        super().__init__()
        self.tower = spring
