from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from util import crop_image, transform_coordinate
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo

if TYPE_CHECKING:
    from model import PartySelector


class PartySelectorView(ObjectBase):
    background_image: pg.Surface
    party_images: dict[None | const.PartyType, pg.Surface] = {}
    ratio: float

    def __init__(self, canvas: pg.Surface, party_selector: PartySelector):
        self.image_initialized = True
        super().__init__(canvas, [const.PRIORITY_PARTY_SELECTOR])
        self.__party_selector = party_selector
        self.__font = pg.font.Font(const.REGULAR_FONT, int(12*ScreenInfo.resize_ratio))

    @classmethod
    def init_convert(cls):
        img = pg.image.load(const.PARTY_SELECTOR_BACKGROUND)

        cls.background_image = crop_image(
            img, *ScreenInfo.screen_size, True).convert_alpha()

        cls.ratio = ScreenInfo.screen_size[0] / 1600
        for key, path in const.PARTY_SELECTOR_IMAGE.items():
            img = pg.image.load(path)
            cls.party_images[key] = crop_image(
                img, 638 * cls.ratio, 260 * cls.ratio).convert_alpha()

        cls.image_initialized = True

    def draw(self):
        point: list = [(107, 124), (107, 527), (868, 124), (868, 527)]
        team_number = 0
        check = 0
        for party in self.__party_selector.selected_parties():
            if party is not None:
                check += 1
            img = self.party_images[party]
            self.canvas.blit(img, transform_coordinate(point[team_number], self.ratio))
            team_number += 1

        img = self.background_image
        self.canvas.blit(img, (0, 0))

        if self.__party_selector.is_ready():
            draw_text(self.canvas, ScreenInfo.screen_size[0] / 2, ScreenInfo.screen_size[1] -
                      40, 'Press ENTER to continue', 'white', self.__font)


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
