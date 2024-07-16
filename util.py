"""
Utility functions that can be utilized across multiple modules.
"""
import base64
import os
import sys
import time

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
    if 5 <= verb < 10:
        print(f"What are you looking for? There is nothing more to print.\n", file=sys.__stdout__)
    elif 10 <= verb < 15:
        print(f"I bet you are a really curious person, but that is not going to work. What you are questing is simply non-existence.\n", file=sys.__stdout__)
    elif 15 <= verb < 20:
        print(f"Alright, but unfortunately, I have nothing to give you. Here is a joke compensating your wasted passion.\n", file=sys.__stdout__)
        print("My mom told me I had no sense of direction, so I packed up my stuff and right.",
              file=sys.__stdout__)
    elif 20 <= verb < 25:
        print(f"It is not gonna work. Give up.\n", file=sys.__stdout__)
    elif 25 <= verb < 30:
        print(f"Do me a favor, go outside and touch some grass. It is really meaningless beyond this point.\n", file=sys.__stdout__)
    elif 30 <= verb < 35:
        print(f"You are not going to give up, are you?\n", file=sys.__stdout__)
    elif 35 <= verb < 40:
        print(f"...\n", file=sys.__stdout__)
    elif 40 <= verb < 45:
        print(f"Stop it. Life is still great and you shouldn't focus on this stupid conversation.\n", file=sys.__stdout__)
    elif 45 <= verb < 50:
        print(f"Anyways.\n", file=sys.__stdout__)
    sleep(1)


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


def sleep(_):
    time.sleep(1)
    if verbosity >= 50:
        print("Finally, the easter egg. I know you are the special one. Go ahead and tell the staff!")
        print(base64.b64decode("ICAgICAgICAgIOKWiOKWiOKWiOKWiOKWiOKWiOKWiOKWiCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICDilojiloggICAgICAgIOKWiOKWiCAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIOKWiOKWiOKWkuKWkuKWkuKWkiAgICAgICAg4paI4paIICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICDilojilojilpLilpLilpLilpLilpLilpIgICAgICDilpLilpLilpLilpLilojiloggICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICDilojilojilpLilpLilpLilpLilpLilpIgICAgICDilpLilpLilpLilpLilojiloggICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAg4paI4paIICDilpLilpLilpLilpIgICAgICAgIOKWkuKWkuKWkuKWkuKWkuKWkuKWiOKWiCAgICAgICAgICAgICAgICAgICAgICAgICAgCiAg4paI4paIICAgICAgICAgICAgICAgIOKWkuKWkuKWkuKWkuKWiOKWiCAgICAgICAgICAgICAgICAgICAgICAgICAgCuKWiOKWiOKWkuKWkiAgICAgIOKWkuKWkuKWkuKWkuKWkuKWkiAgICAgICAgICDilojiloggICAgICAgICAgICAgICAgICAgICAgICAK4paI4paIICAgICAg4paS4paS4paS4paS4paS4paS4paS4paS4paS4paSICAgICAgICDilojiloggICAgICAgICAgICAgICAgICAgICAgICAK4paI4paIICAgICAg4paS4paS4paS4paS4paS4paS4paS4paS4paS4paSICAgIOKWkuKWkuKWkuKWkuKWiOKWiCAgICAgICAgICAgICAgICAgICAgICAgIArilojilojilpLilpLilpLilpIgIOKWkuKWkuKWkuKWkuKWkuKWkuKWkuKWkuKWkuKWkiAg4paS4paS4paS4paS4paS4paS4paI4paIICAgICAgICAgICAgICAgICAgICAgICAgCiAg4paI4paI4paS4paS4paS4paSICDilpLilpLilpLilpLilpLilpIgICAg4paS4paS4paS4paS4paI4paIICAgICAgICAgICAgICAgICAgICAgICAgICAKICDilojilojilpLilpLilpLilpIgICAgICAgICAgICDilpLilpLilpLilpLilojiloggICAgICAgICAgICAgICAgICAgICAgICAgIAogICAg4paI4paI4paS4paSICAgICAgICAgICAgICDilojiloggICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgIOKWiOKWiOKWiOKWiCAgICAgICAg4paI4paI4paI4paIICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICDilojilojilojilojilojilojilojilog=").decode("utf-8"))
