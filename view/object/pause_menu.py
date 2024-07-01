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
        self.title_font = pg.font.Font('./font/Cubic_11_1.300_R.ttf', 48)
        self.font = pg.font.Font('./font/Cubic_11_1.300_R.ttf', 36)
        self.options = self.pause_menu.options

    def draw(self):
        if not self.pause_menu.enabled:
            return
        
        bg_surf = pg.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]), pg.SRCALPHA)
        bg_surf.fill((200, 200, 200, 100))

        center = (bg_surf.get_width() // 2, bg_surf.get_height() // 2)
        
        draw_text(bg_surf, center[0], center[1]-150, 'Paused', 'gray', self.title_font)
        for index, opt_text in enumerate(self.options):
            draw_text(bg_surf, center[0], center[1]+80*index, opt_text, 'gray', self.font, index==self.pause_menu.selected)

        self.canvas.blit(bg_surf, (0, 0))


def draw_text(surf, x, y, text, color, font, underline=False):
    underline_color = 'lightskyblue'
    underline_thickness = 3
    underline_offset = 3
    
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    if underline:
        underline_start = (text_rect.left, text_rect.bottom + underline_offset)
        underline_end = (text_rect.right, text_rect.bottom + underline_offset)
        pg.draw.line(surf, underline_color, underline_start, underline_end, underline_thickness)

    surf.blit(text_surface, text_rect.topleft)