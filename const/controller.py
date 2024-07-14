"""
This module defines constants associated with controller.
"""

from enum import Enum, auto

import pygame as pg

from const.character import CharacterType

DIRECTION_BUTTONS_MAP = {
    pg.K_w: pg.Vector2(0, -1),
    pg.K_s: pg.Vector2(0, 1),
    pg.K_a: pg.Vector2(-1, 0),
    pg.K_d: pg.Vector2(1, 0),
}

TOWER_CHANGE_TYPE_BUTTONS_MAP = {
    pg.K_1: CharacterType.MELEE,
    pg.K_2: CharacterType.RANGER,
    pg.K_3: CharacterType.SNIPER,
}

ABILITY_BUTTON = pg.K_q
CHANGE_TEAM_VISION = pg.K_TAB
TRAJECTORY_SWITCH_BUTTON = pg.K_t
SHOWRANGE_SWITCH_BUTTON = pg.K_r

PAUSE_BUTTON = pg.K_ESCAPE

CONFIRM_BUTTONS = [pg.K_SPACE, pg.K_RETURN]
EGG_SEQ = [pg.K_UP, pg.K_UP, pg.K_DOWN, pg.K_DOWN,
           pg.K_LEFT, pg.K_RIGHT, pg.K_LEFT, pg.K_RIGHT, pg.K_b, pg.K_a]


class PartySelectorInputType(Enum):
    CONFIRM = auto()
    CHANGE = auto()


PARTY_SELECTOR_BUTTONS_MAP: dict[int, tuple[PartySelectorInputType, tuple[int, int] | None]] = {
    pg.K_a: (PartySelectorInputType.CHANGE, (0, -1)),
    pg.K_d: (PartySelectorInputType.CHANGE, (0, 1)),
    pg.K_f: (PartySelectorInputType.CHANGE, (1, -1)),
    pg.K_h: (PartySelectorInputType.CHANGE, (1, 1)),
    pg.K_j: (PartySelectorInputType.CHANGE, (2, -1)),
    pg.K_l: (PartySelectorInputType.CHANGE, (2, 1)),
    pg.K_LEFT: (PartySelectorInputType.CHANGE, (3, -1)),
    pg.K_RIGHT: (PartySelectorInputType.CHANGE, (3, 1)),
    pg.K_SPACE: (PartySelectorInputType.CONFIRM, None),
    pg.K_RETURN: (PartySelectorInputType.CONFIRM, None)
}
"""
Input buttons defined for party-selection process
structure: (operation, (team, operation))
"""
