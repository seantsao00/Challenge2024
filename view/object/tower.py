import pygame as pg

from model.building import Tower
from view.object.entity import Entity


class Tower(Entity):
    def __init__(self, tower: Tower):
        super().__init__()
        self.tower = tower
