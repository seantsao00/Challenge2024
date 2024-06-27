import pygame as pg

import view
from model.entity import Entity


class PauseMenu(Entity):
    def __init__(self):
        super().__init__(self)
        self.view.append(view.PauseMenuView())
        