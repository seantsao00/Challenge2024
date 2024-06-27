from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg


class PauseMenuView:
    def __init__(self):
        pass

    def draw(self, screen: pg.Surface):
        pg.draw.rect(screen, (255, 0, 0), (0, 0, 500, 500))
