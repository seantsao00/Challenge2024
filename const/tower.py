"""
This module defines constants associated with towers.
"""
from dataclasses import dataclass
from enum import Enum, auto


class TowerType(Enum):
    FOUNTAIN = auto()
    HOTEL = auto()
    FERRIES_WHEEL = auto()
    PYLON = auto()


@dataclass(kw_only=True)
class TowerAttribute:
    attack_speed: float
    attack_range: float
    damage: float
    health: float
    vision: float


INITIAL_PERIOD_MS = 5000
FORMULA_K = 1000

TOWER_ATTACK_RANGE = 30
TOWER_ATTACK_PERIOD = 500
TOWER_DAMAGE = 50
TOWER_HEALTH = 1000
TOWER_VISION = 40
