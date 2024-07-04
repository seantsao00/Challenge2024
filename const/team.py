"""
This module defines constants associated with teams.
"""

from enum import Enum, auto

MAX_TEAMS = 4


class InputTypes(Enum):
    PICK = 0
    MOVE = 1
    ATTACK = 2

"""This is for party selection"""
class PartyTypes(Enum):
    JUNIOR = auto()
    FBI = auto()
    POLICE = auto()
    BLACK = auto()
    MAORI = auto()