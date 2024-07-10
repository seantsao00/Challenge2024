from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from util import crop_image
from view.object.object_base import ObjectBase

if TYPE_CHECKING:
    from model import PartySelector


class PartySelectionView(ObjectBase):
    background_image: pg.Surface
    party_images: list[pg.Surface]

    def __init__(self, canvas: pg.Surface, party_selector: PartySelector):
        self.image_initialized = True
        super().__init__(canvas)
        self.__party_selector = party_selector
        self.__font = pg.font.Font(const.REGULAR_FONT, int(12*self.resize_ratio))

    @classmethod
    def init_convert(cls):
        img = pg.image.load(const.PARTY_SELECTION_BACKGROUND)

        cls.background_image = crop_image(img, cls.screen_width, cls.screen_height).convert_alpha()
        cls.image_initialized = True

    def draw(self):
        img = self.background_image
        self.canvas.blit(img, (0, 0))


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
