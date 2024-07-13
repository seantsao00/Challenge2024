import pygame as pg

import const
from instances_manager import get_model
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo
from view.textutil import font_loader


class ClockView(ObjectBase):
    def __init__(self, canvas: pg.Surface):
        super().__init__(canvas, [8])
        self.__canvas = canvas

    def initialize(self):
        pass

    def draw(self):
        time_remaining = int(const.GAME_TIME - get_model().get_time())
        (min, sec) = divmod(time_remaining, 60)
        font = font_loader.get_font(size=20)
        time_remaining_surface = font.render(
            f'{min:02d}:{sec:02d}', False, pg.Color(201, 158, 131))
        self.__canvas.blit(time_remaining_surface, time_remaining_surface.get_rect(
            center=ScreenInfo.translate((50, 30))))
