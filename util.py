"""
Utility functions that can be utilized across multiple modules.
"""

import pygame as pg


def clamp(v, lo, hi):
    if v < lo:
        return lo
    elif v > hi:
        return hi
    else:
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
    if bounding_rect == None:
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
