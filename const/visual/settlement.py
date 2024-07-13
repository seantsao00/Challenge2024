from __future__ import annotations

import os
from math import cos, pi, sin

import pygame as pg

from const.team import PartyType
from const.visual import IMAGE_DIR

SETTLEMENT_DIR = 'settlement/'
SETTLEMENT_BACKGROUND: str = os.path.join(IMAGE_DIR, SETTLEMENT_DIR, 'background.png')
SETTLEMENT_SCOPE: str = os.path.join(IMAGE_DIR, SETTLEMENT_DIR, 'scope.png')
SETTLEMENT_IMAGE: dict[PartyType, str] = {
    PartyType.JUNIOR: os.path.join(IMAGE_DIR, SETTLEMENT_DIR, 'junior.png'),
    PartyType.FBI: os.path.join(IMAGE_DIR, SETTLEMENT_DIR, 'fbi.png'),
    PartyType.POLICE: os.path.join(IMAGE_DIR, SETTLEMENT_DIR, 'police.png'),
    PartyType.BLACK: os.path.join(IMAGE_DIR, SETTLEMENT_DIR, 'black.png'),
    PartyType.MOURI: os.path.join(IMAGE_DIR, SETTLEMENT_DIR, 'mouri.png')
}
SETTLEMENT_TEAM_POSITION: list[pg.Vector2] = [pg.Vector2(
    287, 110), pg.Vector2(36, 430), pg.Vector2(859, 110), pg.Vector2(610, 430)]  # only for scope
SETTLEMENT_INITIAL_POSITION = pg.Vector2(-100, -100)
SCOPE_SPEED = 3
INVERVAL_WAITING = 7
INVERVAL_WANDERING = 5
WANDERING_PERIOD = 3
