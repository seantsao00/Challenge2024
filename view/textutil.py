import pygame as pg

from const import REGULAR_FONT


class __FontLoader:
    """
    Class for things related to font loading/rendering
    """

    def __init__(self):
        self.__fonts: dict[tuple[str, int], pg.font.Font] = {}
        self.__resize_ratio = 1

    def set_resize_ratio(self, resize_ratio: float):
        self.__resize_ratio = resize_ratio

    def get_font(self, name: str | None = REGULAR_FONT, size: int = 12, resize_ratio: float | None = None):
        """
        resize ratio set to default if not given
        """
        if resize_ratio is None:
            resize_ratio = self.__resize_ratio
        size = int(size * resize_ratio)
        if (name, size) not in self.__fonts:
            self.__fonts[(name, size)] = pg.font.Font(name, size)
        return self.__fonts[(name, size)]


font_loader = __FontLoader()


def draw_text(surf: pg.Surface, x: float, y: float, text: str, color: pg.Color, font: pg.font.Font, underline: bool = False):
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
