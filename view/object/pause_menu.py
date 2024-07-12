from __future__ import annotations

import os
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

    def draw(self):
        pause_menu: PauseMenu = self.__pause_menu
        if pause_menu.state is const.PauseMenuState.CLOSED:
            return
        bg_surf = pg.Surface((self.canvas.get_size()), pg.SRCALPHA)
        bg_surf.fill(const.PAUSE_MENU_BACKGROUND_COLOR)

        if pause_menu.state is const.PauseMenuState.MAIN_MENU:
            position = pg.Vector2(const.PAUSE_MENU_TITLE_POSITION) * ScreenInfo.resize_ratio
            interval = const.PAUSE_MENU_OPTION_INTERVAL * ScreenInfo.resize_ratio
            title_font: pg.Font = pg.font.Font(const.REGULAR_FONT, int(20*ScreenInfo.resize_ratio))
            subtitle_font: pg.Font = pg.font.Font(
                const.REGULAR_FONT, int(12*ScreenInfo.resize_ratio))
            draw_text(bg_surf,
                      *position,
                      const.PAUSE_MENU_TITLE_TEXT,
                      const.PAUSE_MENU_TEXT_COLOR,
                      title_font)
            for index, option in enumerate(self.__pause_menu.main_menu_options):
                draw_text(bg_surf,
                          position[0],
                          position[1] + (1+index) * interval,
                          const.PAUSE_MAIN_MENU_TEXT[option],
                          const.PAUSE_MENU_TEXT_COLOR,
                          subtitle_font,
                          index == self.__pause_menu.cursor_index)
        elif pause_menu.state is const.PauseMenuState.CREDIT_BOARD:
            title_font: pg.Font = pg.font.Font(const.REGULAR_FONT, int(10*ScreenInfo.resize_ratio))
            subtitle_font: pg.Font = pg.font.Font(
                const.REGULAR_FONT, int(9*ScreenInfo.resize_ratio))
            content_font: pg.Font = pg.font.Font(
                const.REGULAR_FONT, int(6.5*ScreenInfo.resize_ratio))
            position = pg.Vector2(225, 6) * ScreenInfo.resize_ratio
            blit_normal_text(bg_surf, *position,
                             self.__pause_menu.credit_content.game_title, title_font)
            interval = pg.Vector2(0, 14) * ScreenInfo.resize_ratio
            position += interval
            blit_normal_text(bg_surf, *position,
                             self.__pause_menu.credit_content.title, title_font)
            interval = pg.Vector2(0, 14) * ScreenInfo.resize_ratio
            position += interval

            total_col = 4
            col_interval = pg.Vector2(100, 0) * ScreenInfo.resize_ratio
            for section, names in self.__pause_menu.credit_content.content.items():
                blit_normal_text(bg_surf, *position, section, subtitle_font)
                interval = pg.Vector2(0, 12) * ScreenInfo.resize_ratio
                position += interval
                if section == "Special Thanks":
                    for name in names:
                        blit_normal_text(bg_surf, *position, name, content_font)
                        interval = pg.Vector2(0, 12) * ScreenInfo.resize_ratio
                        position += interval
                else:
                    for i, name in enumerate(names):
                        col = i % total_col
                        displacement = (col - (total_col-1)/2)
                        blit_normal_text(bg_surf, *(position + displacement *
                                         col_interval), name, content_font)
                        if i == len(names) - 1:
                            interval = pg.Vector2(0, 12) * ScreenInfo.resize_ratio
                            position += interval
                        elif col == total_col-1:
                            interval = pg.Vector2(0, 9) * ScreenInfo.resize_ratio
                            position += interval

        self.canvas.blit(bg_surf, (0, 0))


def blit_normal_text(surf: pg.Surface, x: float, y: float, text: str, font: pg.Font, color=const.PAUSE_MENU_TEXT_COLOR):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    surf.blit(text_surface, text_rect.topleft)


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
