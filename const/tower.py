"""
This module defines constants associated with towers.
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, TypeAlias

from const.character import CharacterType
from const.entity import LivingEntityAttribute

if TYPE_CHECKING:
    TowerState: TypeAlias = None


class TowerType(Enum):
    FOUNTAIN = auto()
    HOTEL = auto()
    FERRIS_WHEEL = auto()
    PYLON = auto()


@dataclass(kw_only=True)
class TowerAttribute(LivingEntityAttribute):
    pass


FOUNTAIN_ATTRIBUTE = TowerAttribute(
    attack_damage=150,
    attack_speed=1,
    attack_range=40,
    max_health=1000,
    vision=40
)

NEUTRAL_TOWER_ATTRIBUTE = TowerAttribute(
    attack_damage=150,
    attack_speed=1,
    attack_range=40,
    max_health=1000,
    vision=40
)

TOWER_DEFAULT_GENERATE_CHARACTER = CharacterType.RANGER
TOWER_GENERATE_DISPLACEMENT = 10
"""The distance between generated character and the tower will be less than this value."""

INITIAL_PERIOD_MS = 1000
FORMULA_K = 1000

def COUNT_PERIOD_MS(entity_number):
    return INITIAL_PERIOD_MS * (1 + (entity_number / 40) ** (2.5))
