from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_PAUSEMENU
from view.object.object_base import ObjectBase
from view.textutil import draw_text, font_loader

if TYPE_CHECKING:
    from model import PauseMenu


class PauseMenuView(ObjectBase):
    def __init__(self, canvas: pg.Surface, pause_menu: PauseMenu):
        self.image_initialized = True
        super().__init__(canvas, [PRIORITY_PAUSEMENU])
        self.pause_menu = pause_menu
        self.title_font = font_loader.get_font(size=12)
        self.font = font_loader.get_font(size=12)
        self.options = self.pause_menu.options

    def draw(self):
        if not self.pause_menu.enabled:
            return

        bg_surf = pg.Surface((self.canvas.get_size()), pg.SRCALPHA)
        bg_surf.fill((200, 200, 200, 230))

        center = (bg_surf.get_width() // 2, bg_surf.get_height() // 2)

        draw_text(bg_surf, center[0], center[1]-150, 'Paused', 'black', self.title_font)
        for index, opt_text in enumerate(self.options):
            draw_text(bg_surf, center[0], center[1]+80*index, opt_text,
                      'black', self.font, index == self.pause_menu.selected)

        self.canvas.blit(bg_surf, (0, 0))
