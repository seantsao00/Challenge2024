"""
This module defines constants associated with model.
"""

from enum import Enum, auto

FPS = 60


class State(Enum):
    """States of the game."""
    MENU = auto()
    PLAY = auto()
    PAUSE = auto()
