"""
This module defines constants associated with bullets.
"""
from enum import Enum, auto
from typing import TYPE_CHECKING, TypeAlias

BULLET_SPEED = 10
BULLET_INTERVAL = 5

class BulletType(Enum):
    EXPLODE = auto()
    RANGER = auto()
    SNIPER = auto()

if TYPE_CHECKING:
    BulletState: TypeAlias = None
