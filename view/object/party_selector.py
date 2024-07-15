from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from util import crop_image, transform_coordinate
from view.object.object_base import ObjectBase
from view.screen_info import ScreenInfo
from view.textutil import draw_text, font_loader

if TYPE_CHECKING:
    from model import PartySelector


class PartySelectorView(ObjectBase):
    background_image: pg.Surface
    bottom_image: pg.Surface
    party_images: dict[None | const.PartyType, pg.Surface] = {}
    ratio: float

    def __init__(self, canvas: pg.Surface, party_selector: PartySelector):
        self.image_initialized = True
        super().__init__(canvas, [const.PRIORITY_PARTY_SELECTOR])
        self.__party_selector = party_selector
        self.__font = font_loader.get_font(size=12)

    @classmethod
    def init_convert(cls):
        img = pg.image.load(const.PARTY_SELECTOR_BACKGROUND)

        cls.background_image = crop_image(
            img, *ScreenInfo.screen_size, True).convert_alpha()

        img = pg.image.load(const.PARTY_SELECTOR_BOTTOM)
        cls.bottom_image = crop_image(
            img, *ScreenInfo.screen_size, True).convert_alpha()

        cls.ratio = ScreenInfo.screen_size[0] / 1600
        for key, path in const.PARTY_SELECTOR_IMAGE.items():
            img = pg.image.load(path)
            cls.party_images[key] = crop_image(
                img, 638 * cls.ratio, 260 * cls.ratio).convert_alpha()

        cls.image_initialized = True

    def draw(self):
        img = self.bottom_image
        self.canvas.blit(img, (0, 0))

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
                      40, 'Press SPACE/ENTER to continue', 'white', self.__font)
