import pygame as pg

from const import REGULAR_FONT
from view.screen_info import ScreenInfo


class __FontLoader:
    """
    Class for things related to font loading/rendering
    """

    def __init__(self):
        self.__fonts: dict[tuple[str, int], pg.font.Font] = {}

    def get_font(self, name: str | None = REGULAR_FONT, size: int = 12, resize_ratio: float | None = None):
        """
        resize ratio set to default if not given
        """
        if resize_ratio is None:
            resize_ratio = ScreenInfo.resize_ratio
        size = int(size * resize_ratio)
        if (name, size) not in self.__fonts:
            self.__fonts[(name, size)] = pg.font.Font(name, size)
        return self.__fonts[(name, size)]


font_loader = __FontLoader()


def draw_text(surf: pg.Surface, x: float, y: float, text: str, color: pg.Color, font: pg.font.Font, underline: bool = False, align_text: str = 'center'):
    underline_color = 'darkblue'
    underline_thickness = 3
    underline_offset = 3

    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(**{align_text: (x, y)})

    if underline:
        underline_start = (text_rect.left, text_rect.bottom + underline_offset)
        underline_end = (text_rect.right, text_rect.bottom + underline_offset)
        pg.draw.line(surf, underline_color, underline_start, underline_end, underline_thickness)

    surf.blit(text_surface, text_rect.topleft)


def split_text(text: str, font: pg.font.Font, max_width: float, delimiter: str = ' ') -> list[str]:
    """
    Split the text into lines so that each line fits in the width constraint.

    When tokenize is True, text is first splitted by spaces into tokens; the
    same token will not be placed in different lines except for when a token
    is too long to display in a single line.
    Line breaks ('\n') are preserved.
    """
    if '\n' in text:
        lines = []
        for ln in text.split('\n'):
            lines += split_text(ln.strip(), font, max_width, delimiter)
        return lines

    tokens: list[str] = []
    if len(delimiter):
        tokens = text.split(delimiter)
    else:
        tokens = list(text)

    lines = [""]
    while len(tokens):
        tok = tokens[0]
        last_line = lines[-1] + (delimiter if len(lines[-1]) > 0 else "") + tok
        if font.size(last_line)[0] <= max_width:
            lines[-1] = last_line
            del tokens[0]
        elif len(lines[-1]) > 0:
            lines.append("")
        else:
            lines = lines[:-1] + split_text(tok, font, max_width, delimiter="")
            del tokens[0]
    return lines
