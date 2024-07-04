"""
This module defines constants associated with parties.
"""

from enum import Enum, auto

MAX_PARTIES = 5

class PartyTypes(Enum):
    JUNIOR = auto()
    FBI = auto()
    POLICE = auto()
    BLACK = auto()
    MAORI = auto()
