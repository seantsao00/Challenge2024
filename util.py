"""
Utility functions that can be utilized across multiple modules.
"""
import os
import sys

import cv2
import pygame as pg


def clamp(v, lo, hi):
    if v < lo:
        return lo
    if v > hi:
        return hi
    return v


def crop_image(picture: pg.Surface, desire_width: int, desire_height: int,
               large: bool = False, bounding_rect: pg.Rect = None) -> pg.Surface:
    """
    Remove redundant transparent part of the image to creating a minimal rectangle and
    scale the image to desired size without changing the ratio of its width and height.

    * If `large == False`, the size of cropped image won't be bigger than the desired size.
    * If `large == True`, the size of cropped image won't be smaller than the desired size.
    """
    image = picture
    if bounding_rect is None:
        bounding_rect = image.get_bounding_rect()
    cropped_image = pg.Surface(bounding_rect.size, pg.SRCALPHA)
    cropped_image.blit(image, (0, 0), bounding_rect)
    width, height = [cropped_image.get_width(), cropped_image.get_height()]
    if large:
        ratio = max(desire_width/width, desire_height/height)
    else:
        ratio = min(desire_width/width, desire_height/height)
    cropped_image = pg.transform.scale(
        cropped_image, (width*ratio, height*ratio))
    return cropped_image


verbosity = 0


def disable_print():
    sys.stdout = open(os.devnull, 'w')


def set_verbosity(verb: int):
    global verbosity
    verbosity = verb


def log_critical(msg: str):
    """Print critical logging message."""
    print(f"\033[91m[Crit] {msg}\033[0m", file=sys.__stdout__)


def log_warning(msg: str):
    """Print warning logging message."""
    if verbosity >= 1:
        print(f"\033[93m[Warn] {msg}\033[0m", file=sys.__stdout__)


def log_info(msg: str):
    """Print info logging message."""
    if verbosity >= 2:
        print(f"[Info] {msg}", file=sys.__stdout__)


def transform_coordinate(point: tuple[float, float], ratio: float) -> tuple[float, float]:
    x, y = point
    return (x * ratio, y * ratio)


def load_image(filepath: str, width: int, height: int) -> tuple[pg.Surface, pg.Vector2]:
    """
    Load_image and resize it to the desired size.
    Return the image and the left top position of the result surface.
    This function WON'T ignore transparent part of the image.
    """
    assert isinstance(width, int) and isinstance(height, int)
    loaded_image = cv2.imread(
        filepath, cv2.IMREAD_UNCHANGED
    )
    loaded_image = cv2.resize(
        loaded_image, (width, height), interpolation=cv2.INTER_AREA
    )
    x, y, w, h = cv2.boundingRect(loaded_image[..., 3])
    picture = pg.image.load(filepath).convert_alpha()
    picture = pg.transform.scale(picture, (width, height))
    picture = picture.subsurface(pg.Rect(x, y, w, h))
    return (picture, pg.Vector2(x, y))
