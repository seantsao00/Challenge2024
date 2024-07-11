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
BULLET_COMMON_SPEED = 50
BULLET_RANGER_SPEED = 50
BULLET_SNIPER_SPEED = 180
BULLET_SNIPER_ATTACK_TOWER_DEBUFF = 5
BULLET_RANGER_ABILITY_DURATION = 0.15
