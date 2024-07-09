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

PAUSE_BUTTON = pg.K_ESCAPE

LEAVE_COVER_BUTTON = pg.K_SPACE


class PartySelectInput(Enum):
    CONFIRM = auto()
    CHANGE = auto()


PARTY_SELECT_BUTTONS_MAP: dict[int, tuple[PartySelectInput, tuple[int, int] | None]] = {
    pg.K_a: (PartySelectInput.CHANGE, (1, -1)),
    pg.K_d: (PartySelectInput.CHANGE, (1, 1)),
    pg.K_f: (PartySelectInput.CHANGE, (2, -1)),
    pg.K_h: (PartySelectInput.CHANGE, (2, 1)),
    pg.K_j: (PartySelectInput.CHANGE, (3, -1)),
    pg.K_l: (PartySelectInput.CHANGE, (3, 1)),
    pg.K_LEFT: (PartySelectInput.CHANGE, (4, -1)),
    pg.K_RIGHT: (PartySelectInput.CHANGE, (4, 1)),
    pg.K_SPACE: (PartySelectInput.CONFIRM, None),
    pg.K_RETURN: (PartySelectInput.CONFIRM, None)
}
"""
Input buttons defined for party-selection process
structure: (operation, (team, operation))
"""
