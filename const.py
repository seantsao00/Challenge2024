from enum import Enum, IntEnum, auto

import pygame as pg


# model-start


FPS = 60


class State(Enum):
    """States of the game."""
    MENU = auto()
    PLAY = auto()
    PAUSE = auto()


# model-end


# character-start


PLAYER_SPEED = 100


# character-end


# controller-start


PLAYER_KEYS = {
    pg.K_w: pg.Vector2(0, -1),
    pg.K_s: pg.Vector2(0, 1),
    pg.K_a: pg.Vector2(-1, 0),
    pg.K_d: pg.Vector2(1, 0),
}


# control-end
