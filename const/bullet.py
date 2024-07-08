"""
This module defines constants associated with bullets.
"""
from enum import Enum, auto
from typing import TYPE_CHECKING, TypeAlias

class BulletType(Enum):
    COMMON = auto()
    SNIPER = auto()
    RANGER = auto()
    EXPLODE = auto()

if TYPE_CHECKING:
    BulletState: TypeAlias = None

BULLET_COMMON_SPEED = 10
BULLET_RANGER_SPEED = 10
BULLET_SNIPER_SPEED = 10
BULLET_INTERVAL = 5
