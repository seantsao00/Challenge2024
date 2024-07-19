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
    NEUTRAL = auto()
    """中立"""

    JUNIOR = auto()
    """少年偵探團"""

    FBI = auto()
    """FBI"""

    POLICE = auto()
    """警視廳"""

    BLACK = auto()
    """黑衣組織"""

    MOURI = auto()
    """毛利偵探事務所"""

    KIDDO = auto()
    """基德家族"""
