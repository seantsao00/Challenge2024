"""
This module defines constants associated with towers.
"""
from dataclasses import dataclass
from enum import Enum, auto

from const.character import CharacterType
from const.entity import LivingEntityAttribute


class TowerType(Enum):
    FOUNTAIN = auto()
    HOTEL = auto()
    FERRIS_WHEEL = auto()
    PYLON = auto()


@dataclass(kw_only=True)
class TowerAttribute(LivingEntityAttribute):
    pass


class TowerState(Enum):
    pass


FOUNTAIN_ATTRIBUTE = TowerAttribute(
    attack_damage=150,
    attack_speed=1,
    attack_range=45,
    max_health=1000,
    vision=45
)

NEUTRAL_TOWER_ATTRIBUTE = TowerAttribute(
    attack_damage=150,
    attack_speed=1,
    attack_range=45,
    max_health=1000,
    vision=45
)

TOWER_DEFAULT_GENERATE_CHARACTER = CharacterType.RANGER
TOWER_GENERATE_DISPLACEMENT = 5
"""The distance between generated character and the tower will be less than this value."""

TOWER_SPAWN_INITIAL_PERIOD = 1
"""The initial period of tower to spawn in second."""


def count_period_ms(entity_number: int) -> float:
    return TOWER_SPAWN_INITIAL_PERIOD * (1 + (entity_number / 10) ** (2))
