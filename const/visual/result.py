from __future__ import annotations

import os
from enum import Enum, auto
from math import cos, sin
from random import randint, uniform

import pygame as pg

from const.team import PartyType
from const.visual import IMAGE_DIR

RESULT_DIR = 'result/'
RESULT_BACKGROUND: str = os.path.join(IMAGE_DIR, RESULT_DIR, 'background.png')
RESULT_BOTTOM: str = os.path.join(IMAGE_DIR, RESULT_DIR, 'bottom.png')
RESULT_SCOPE: str = os.path.join(IMAGE_DIR, RESULT_DIR, 'scope.png')
RESULT_OUT: str = os.path.join(IMAGE_DIR, RESULT_DIR, 'out_icon.png')
RESULT_GOLDCIRCLE: str = os.path.join(IMAGE_DIR, RESULT_DIR, 'gold_circle.png')
RESULT_CROWN: str = os.path.join(IMAGE_DIR, RESULT_DIR, 'crown.png')
RESULT_IMAGE_NOMAL: dict[PartyType, str] = {
    PartyType.JUNIOR: os.path.join(IMAGE_DIR, RESULT_DIR, 'junior.png'),
    PartyType.FBI: os.path.join(IMAGE_DIR, RESULT_DIR, 'fbi.png'),
    PartyType.POLICE: os.path.join(IMAGE_DIR, RESULT_DIR, 'police.png'),
    PartyType.BLACK: os.path.join(IMAGE_DIR, RESULT_DIR, 'black.png'),
    PartyType.MOURI: os.path.join(IMAGE_DIR, RESULT_DIR, 'mouri.png')
}
RESULT_IMAGE_GRAY: dict[PartyType, str] = {
    PartyType.JUNIOR: os.path.join(IMAGE_DIR, RESULT_DIR, 'junior_gray.png'),
    PartyType.FBI: os.path.join(IMAGE_DIR, RESULT_DIR, 'fbi_gray.png'),
    PartyType.POLICE: os.path.join(IMAGE_DIR, RESULT_DIR, 'police_gray.png'),
    PartyType.BLACK: os.path.join(IMAGE_DIR, RESULT_DIR, 'black_gray.png'),
    PartyType.MOURI: os.path.join(IMAGE_DIR, RESULT_DIR, 'mouri_gray.png')
}
RESULT_TEAM_POSITION: list[pg.Vector2] = [pg.Vector2(
    287, 110), pg.Vector2(36, 430), pg.Vector2(859, 110), pg.Vector2(610, 430)]  # only for scope
RESULT_INITIAL_POSITION: pg.Vector2 = pg.Vector2(-300, -300)
RESULT_FINAL_POSITION: pg.Vector2 = pg.Vector2(1000, 1000)


class ScopeStatus(Enum):
    WAITING_INPUT = auto()
    WANDERING = auto()
    FINAL_WANDERING = auto()
    WAITING = auto()
    TOWARD_TARGET = auto()
    TOWARD_WANDERING = auto()
    FINISH = auto()


SCOPE_SPEED = 7
INVERVAL_WAITING = 1
INVERVAL_WANDERING = uniform(4.0, 6.5)
WANDERING_PERIOD = 3
POSITION_EPSILON = 0.01


def final_wanderring_parameter() -> int:
    return randint(0, 2)


def wandering_formula(t: float) -> pg.Vector2:
    return pg.Vector2(200*cos(t)+450, 100*sin(2*t)+280)
