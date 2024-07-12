from __future__ import annotations

import os

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
    284, 100), pg.Vector2(33, 420), pg.Vector2(851, 100), pg.Vector2(600, 420)]
SETTLEMENT_INITIAL_POSITION = pg.Vector2(-100, -100)
SCOPE_SPEED = 3
