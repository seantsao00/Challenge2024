from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from instances_manager import get_model
from util import crop_image, transform_coordinate
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo


class SettlementView(ObjectBase):
    background_image: pg.Surface
    party_images: dict[const.PartyType, pg.Surface] = {}
    ratio: float

    def __init__(self, canvas: pg.Surface):
        self.image_initialized = True
        super().__init__(canvas, [const.PRIORITY_SETTLEMENT])
        self.__font = pg.font.Font(const.REGULAR_FONT, int(12*ScreenInfo.resize_ratio))
        self.__scope_position = pg.Vector2(-100, -100)

    @classmethod
    def init_convert(cls):
        img = pg.image.load(const.SETTLEMENT_BACKGROUND)

        cls.ratio = ScreenInfo.screen_size[1] / 900

        cls.background_image = crop_image(
            img, 1260 * cls.ratio, ScreenInfo.screen_size[1], True).convert_alpha()

        for key, path in const.SETTLEMENT_IMAGE.items():
            img = pg.image.load(path)
            cls.party_images[key] = crop_image(
                img, 376 * cls.ratio, 360 * cls.ratio).convert_alpha()

        cls.image_initialized = True

    def draw(self):
        model = get_model()
        point: list = [(284, 100), (33, 420), (600, 420), (851, 100)]
        team_number = 0
        for team in model.teams:
            img = self.party_images[team.party]
            self.canvas.blit(img, transform_coordinate(point[team_number], self.ratio))
            team_number += 1

        img = self.background_image
        self.canvas.blit(img, (0, 0))

        # if self.__party_selector.is_ready():
        #     draw_text(self.canvas, ScreenInfo.screen_size[0] / 2, ScreenInfo.screen_size[1] -
        #               40, 'Press ENTER to continue', 'white', self.__font)

    def update(self) -> bool:

        return True


def draw_text(surf: pg.Surface, x: float, y: float, text: str, color, font: pg.Font, underline: bool = False):
    underline_color = 'darkblue'
    underline_thickness = 3
    underline_offset = 3

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))

    if underline:
        underline_start = (text_rect.left, text_rect.bottom + underline_offset)
        underline_end = (text_rect.right, text_rect.bottom + underline_offset)
        pg.draw.line(surf, underline_color, underline_start, underline_end, underline_thickness)

    surf.blit(text_surface, text_rect.topleft)
