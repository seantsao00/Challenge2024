from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg
from const import WINDOW_SIZE

if TYPE_CHECKING:
    from model import PauseMenu


class PauseMenuView:
    def __init__(self, pause_menu: PauseMenu, canvas: pg.Surface):
        self.pause_menu = pause_menu
        self.canvas = canvas
        self.font = pg.font.Font('./font/Cubic_11_1.300_R.ttf', 48)

    def draw(self):
        if not self.pause_menu.enabled:
            pass
        bg_surf = pg.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]), pg.SRCALPHA)
        bg_surf.fill((200, 200, 200, 100))

        text_surface = self.font.render('Paused', True, 'gray')
        bg_surf.blit(text_surface, (
            (bg_surf.get_width() - text_surface.get_width()) // 2,
            (bg_surf.get_height() - text_surface.get_height()) // 2
        ))

        self.canvas.blit(bg_surf, (0, 0))
        
