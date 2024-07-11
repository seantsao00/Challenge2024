from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from util import crop_image, transform_coordinate
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import PartySelector


class PartySelectionView(ObjectBase):
    background_image: pg.Surface
    party_images: dict[None | const.PartyType, pg.Surface] = {}
    ratio: float

    def __init__(self, canvas: pg.Surface, party_selector: PartySelector):
        self.image_initialized = True
        super().__init__(canvas, [const.PRIORITY_PARTYSELECTION])
        self.__party_selector = party_selector

    @classmethod
    def init_convert(cls):
        img = pg.image.load(const.PARTY_SELECTION_BACKGROUND)

        cls.background_image = crop_image(
            img, cls.screen_width, cls.screen_height, True).convert_alpha()

        cls.ratio = cls.screen_width / 1600
        for key, path in const.PARTY_SELECTION_IMAGE.items():
            img = pg.image.load(path)
            cls.party_images[key] = crop_image(
                img, 638 * cls.ratio, 260 * cls.ratio).convert_alpha()

        cls.image_initialized = True

    def draw(self):
        point: list = [(107, 124), (107, 527), (868, 124), (868, 527)]
        team_number = 0
        for party in self.__party_selector.selected_parties():
            img = self.party_images[party]
            self.canvas.blit(img, transform_coordinate(point[team_number], self.ratio))
            team_number += 1

        img = self.background_image
        self.canvas.blit(img, (0, 0))
