"""
This module defines constants associated with towers.
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    TowerState: TypeAlias = None


class TowerType(Enum):
    FOUNTAIN = auto()
    HOTEL = auto()
    FERRIES_WHEEL = auto()
    PYLON = auto()


@dataclass(kw_only=True)
class TowerAttribute:
    attack_damage: float
    attack_speed: float
    attack_range: float
    max_health: float | None
    vision: float


FOUNTAIN_ATTRIBUTE = TowerAttribute(
    attack_damage=50,
    attack_speed=0.5,
    attack_range=30,
    max_health=None,
    vision=40
)

NEUTRAL_TOWER_ATTRIBUTE = TowerAttribute(
    attack_damage=50,
    attack_speed=0.5,
    attack_range=30,
    max_health=1000,
    vision=40
)

INITIAL_PERIOD_MS = 5000
FORMULA_K = 1000

TOWER_ATTACK_RANGE = 30
TOWER_ATTACK_PERIOD = 500
TOWER_DAMAGE = 50
TOWER_HEALTH = 1000
TOWER_VISION = 40
