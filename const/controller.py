"""
This module defines constants associated with controller.
"""

import pygame as pg

HUMAN_KEYS_MAP = {
    pg.K_w: pg.Vector2(0, -1),
    pg.K_s: pg.Vector2(0, 1),
    pg.K_a: pg.Vector2(-1, 0),
    pg.K_d: pg.Vector2(1, 0),
}

PAUSE_BUTTON = pg.K_ESCAPE

START_BUTTON = pg.K_SPACE
