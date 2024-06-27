import pygame as pg

import view
from model.entity import Entity


class PauseMenu:
    def __init__(self):
        self.enabled: bool = True # to be renamed
        