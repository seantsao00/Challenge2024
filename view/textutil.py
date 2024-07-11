import pygame as pg


class FontManager:
    def __init__(self):
        self.__fonts: dict[tuple[str, int], pg.font.Font] = {}

    def get_font(self, name: str | None, size: int):
        if (name, size) not in self.__fonts:
            self.__fonts[(name, size)] = pg.font.Font(name, size)
        return self.__fonts[(name, size)]


__manager = FontManager()


def get_font(name: str | None, size: int):
    return __manager.get_font(name, size)


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
