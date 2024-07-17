from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pygame as pg

import const
from const.visual.priority import PRIORITY_NYAN
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import Nyan


class NyanView(ObjectBase):
    def __init__(self, canvas: pg.Surface, nyan: Nyan):
        super().__init__(canvas, [PRIORITY_NYAN])
        self.__nyan: Nyan = nyan
        self.font = pg.font.Font(const.REGULAR_FONT, int(6*ScreenInfo.resize_ratio))
        self.cat_image = pg.transform.scale(pg.transform.flip(pg.image.load(os.path.join(
            const.IMAGE_DIR, 'entity', 'nyan', 'nyan.png')).convert_alpha(), True, False), pg.Vector2(38.4, 24) * ScreenInfo.resize_ratio)
        self.rainbow_image = pg.transform.scale(pg.transform.flip(pg.image.load(os.path.join(
            const.IMAGE_DIR, 'entity', 'nyan', 'rainbow.png')).convert_alpha(), True, False), pg.Vector2(128, 13) * ScreenInfo.resize_ratio)

    def draw(self):
        nyan: Nyan = self.__nyan
        if not nyan.enabled:
            return
        self.canvas.blit(self.rainbow_image, (nyan.position +
                         pg.Vector2(30, 5)) * ScreenInfo.resize_ratio)
        self.canvas.blit(self.cat_image, nyan.position * ScreenInfo.resize_ratio)
        # 請在遊戲內觸發此彩蛋
        text_surface = self.font.render('恭喜找到彩蛋，成功觸發請通知 Hyper', True, (0, 0, 0))
        text_rect = text_surface.get_rect(midleft=((nyan.position +
                                                    pg.Vector2(40, 12))*ScreenInfo.resize_ratio))
        self.canvas.blit(text_surface, text_rect.topleft)
