"""
This module defines constants associated with teams.
"""

from enum import Enum

MAX_TEAMS = 4


class InputTypes(Enum):
    PICK = 0
    MOVE = 1
    ATTACK = 2
    ABILITIES = 3

class CharTypes(Enum):
    NONE = 0
    TOWER = 1
    CHAR = 2