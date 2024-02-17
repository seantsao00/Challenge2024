"""
This module defines constants associated with controller.
"""

import pygame as pg

from const.player import PlayerIds

PLAYER_KEYS_MAP = {
    PlayerIds.PLAYER0: {
        pg.K_w: pg.Vector2(0, -1),
        pg.K_s: pg.Vector2(0, 1),
        pg.K_a: pg.Vector2(-1, 0),
        pg.K_d: pg.Vector2(1, 0),
    }
}
