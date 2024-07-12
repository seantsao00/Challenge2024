from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_PAUSEMENU
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import PauseMenu


class PauseMenuView(ObjectBase):
    def __init__(self, canvas: pg.Surface, pause_menu: PauseMenu):
        super().__init__(canvas, [PRIORITY_PAUSEMENU])
        self.__pause_menu: PauseMenu = pause_menu
        self.title_font: pg.Font = pg.font.Font(
            const.REGULAR_FONT, int(20*ScreenInfo.resize_ratio))
        self.font: pg.Font = pg.font.Font(const.REGULAR_FONT, int(12*ScreenInfo.resize_ratio))

    def draw(self):
        pause_menu: PauseMenu = self.__pause_menu
        if pause_menu.state is const.PauseMenuState.CLOSED:
            return
        bg_surf = pg.Surface((self.canvas.get_size()), pg.SRCALPHA)
        bg_surf.fill(const.PAUSE_MENU_BACKGROUND_COLOR)
        position = pg.Vector2(const.PAUSE_MENU_TITLE_POSITION) * ScreenInfo.resize_ratio
        interval = const.PAUSE_MENU_OPTION_INTERVAL * ScreenInfo.resize_ratio

        if pause_menu.state is const.PauseMenuState.MAIN_MENU:
            draw_text(bg_surf,
                      *position,
                      const.PAUSE_MENU_TITLE_TEXT,
                      const.PAUSE_MENU_TEXT_COLOR,
                      self.title_font)
            for index, option in enumerate(self.__pause_menu.main_menu_options):
                draw_text(bg_surf,
                          position[0],
                          position[1] + (1+index) * interval,
                          const.PAUSE_MAIN_MENU_TEXT[option],
                          const.PAUSE_MENU_TEXT_COLOR,
                          self.font,
                          index == self.__pause_menu.cursor_index)

        self.canvas.blit(bg_surf, (0, 0))


def draw_text(surf: pg.Surface, x: float, y: float, text: str, color, font: pg.Font, underline: bool = False):
    underline_color = const.PAUSE_MENU_UNDERLINE_COLOR
    underline_thickness = const.PAUSE_MENU_UNDERLINE_THICKNESS
    underline_offset = const.PAUSE_MENU_UNDERLINE_OFFSET

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    if underline:
        underline_start = (text_rect.left, text_rect.bottom + underline_offset)
        underline_end = (text_rect.right, text_rect.bottom + underline_offset)
        pg.draw.line(surf, underline_color, underline_start, underline_end, underline_thickness)

    surf.blit(text_surface, text_rect.topleft)
