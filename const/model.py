"""
This module defines constants associated with model.
"""

from enum import Enum, auto

FPS = 60

# the total game time is 3 minutes
GAME_TIME = 180


class State(Enum):
    """States of the game."""
    COVER = auto()
    SELECT_PARTY = auto()
    PLAY = auto()
    PAUSE = auto()
