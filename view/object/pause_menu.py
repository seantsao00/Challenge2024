from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

if TYPE_CHECKING:
    from model import PauseMenu


class PauseMenuView:
    def __init__(self, pause_menu: PauseMenu, canvas: pg.Surface):
        self.pause_menu = pause_menu
        self.canvas = canvas

    def draw(self):
        if self.pause_menu.enabled:
            pass
        pg.draw.rect(self.canvas, (255, 0, 0), (0, 0, 500, 500))
