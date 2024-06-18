import pygame as pg

import model.spring
from view.object.entity import Entity
import model


class Tower(Entity):
    def __init__(self, spring: model.spring):
        super().__init__()
        self.tower = spring
