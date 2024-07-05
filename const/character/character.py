"""
This module defines constants associated with characters.
"""

from enum import Enum, auto


class CharacterType(Enum):
    MELEE = auto()
    RANGER = auto()
    SNIPER = auto()
