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

""" input buttons defined for party-selection process"""
PARTY_KEYS_MAP = {
    'team1': {
        'left': pg.K_r,
        'right': pg.K_f,
        'enter': pg.K_v
    },
    'team2': {
        'left': pg.K_t,
        'right': pg.K_g,
        'enter': pg.K_b
    },
    'team3': {
        'left': pg.K_y,
        'right': pg.K_h,
        'enter': pg.K_n
    },
    'team4': {
        'left': pg.K_u,
        'right': pg.K_j,
        'enter': pg.K_m
    }
}