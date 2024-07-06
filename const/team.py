"""
This module defines constants associated with teams.
"""

from enum import Enum, IntEnum, auto

MAX_TEAMS = 4


class InputTypes(Enum):
    PICK = auto()
    MOVE = auto()
    ATTACK = auto()
    ABILITIES = auto()


class CharTypes(Enum):
    NONE = auto()
    TOWER = auto()
    CHAR = auto()


class PartyTypes(IntEnum):
    """This is for party selection"""
    JUNIOR = auto()
    FBI = auto()
    POLICE = auto()
    BLACK = auto()
    MAORI = auto()
