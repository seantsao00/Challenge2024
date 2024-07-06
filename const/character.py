"""
This module defines constants associated with characters.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    CharacterState: TypeAlias = None


class CharacterType(Enum):
    MELEE = auto()
    RANGER = auto()
    SNIPER = auto()


@dataclass(kw_only=True)
class CharacterAttribute:
    attack_damage: float
    attack_speed: float
    attack_range: float
    max_health: float
    vision: float
    speed: float
    ability_variable: float
    ability_cd: float | None


MELEE_ATTRIBUTE = CharacterAttribute(
    speed=2,
    attack_range=10,
    attack_damage=75,
    max_health=500,
    vision=30,
    ability_variable=5,
    ability_cd=1.5,
    attack_speed=0.8
)

RANGER_ATTRIBUTE = CharacterAttribute(
    speed=2,
    attack_range=25,
    attack_damage=50,
    max_health=200,
    vision=30,
    ability_variable=100,
    ability_cd=1.5,
    attack_speed=1
)

SNIPER_ATTRIBUTE = CharacterAttribute(
    speed=1.5,
    attack_range=50,
    attack_damage=150,
    max_health=300,
    vision=50,
    ability_variable=None,
    ability_cd=1.5,
    attack_speed=0.5
)
