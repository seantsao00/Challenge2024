"""
This module defines constants associated with teams.
"""

from enum import Enum, auto

MAX_TEAMS = 4


class InputTypes(Enum):
    PICK = auto()
    MOVE = auto()
    ATTACK = auto()
    ABILITY = auto()


class PartyType(Enum):
    """This is for party selection"""
    NEUTRAL = auto()
    JUNIOR = auto()
    FBI = auto()
    POLICE = auto()
    BLACK = auto()
    MOURI = auto()
