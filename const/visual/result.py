from __future__ import annotations

import os
from enum import Enum, auto
from math import cos, pi, sin

import pygame as pg

from const.team import PartyType
from const.visual import IMAGE_DIR

RESULT_DIR = 'result/'
RESULT_BACKGROUND: str = os.path.join(IMAGE_DIR, RESULT_DIR, 'background.png')
RESULT_BOTTOM: str = os.path.join(IMAGE_DIR, RESULT_DIR, 'bottom.png')
RESULT_SCOPE: str = os.path.join(IMAGE_DIR, RESULT_DIR, 'scope.png')
RESULT_IMAGE: dict[PartyType, str] = {
    PartyType.JUNIOR: os.path.join(IMAGE_DIR, RESULT_DIR, 'junior.png'),
    PartyType.FBI: os.path.join(IMAGE_DIR, RESULT_DIR, 'fbi.png'),
    PartyType.POLICE: os.path.join(IMAGE_DIR, RESULT_DIR, 'police.png'),
    PartyType.BLACK: os.path.join(IMAGE_DIR, RESULT_DIR, 'black.png'),
    PartyType.MOURI: os.path.join(IMAGE_DIR, RESULT_DIR, 'mouri.png')
}
RESULT_TEAM_POSITION: list[pg.Vector2] = [pg.Vector2(
    287, 110), pg.Vector2(36, 430), pg.Vector2(859, 110), pg.Vector2(610, 430)]  # only for scope
RESULT_INITIAL_POSITION: pg.Vector2 = pg.Vector2(-100, -100)
RESULT_FINAL_POSITION: pg.Vector2 = pg.Vector2(1000, 1000)


class ScopeStatus(Enum):
    WANDERING = auto()
    WAITING = auto()
    TOWARD_TARGET = auto()
    TOWARD_WANDERING = auto()
    FINISH = auto()


SCOPE_SPEED = 3
INVERVAL_WAITING = 7
INVERVAL_WANDERING = 5
WANDERING_PERIOD = 3
POSITION_EPSILON = 0.01
