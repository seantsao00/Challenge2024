"""
This module defines constants associated with bullets.
"""
from enum import Enum, auto
from typing import TYPE_CHECKING, TypeAlias


class BulletType(Enum):
    COMMON = auto()
    SNIPER = auto()
    RANGER = auto()


class BulletState(Enum):
    FLYING = auto()
    EXPLODE = auto()


# Make Speed smaller to make the effect more obvious
BULLET_COMMON_SPEED = 1
BULLET_RANGER_SPEED = 1
BULLET_SNIPER_SPEED = 3.5
BULLET_SNIPER_ATTACK_TOWER_DEBUFF = 5
