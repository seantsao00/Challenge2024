import pygame as pg

import model
from model.building import Fountain
from view.object.entity import Entity


class Tower(Entity):
    def __init__(self, fountain: Fountain):
        super().__init__()
        self.tower = fountain
