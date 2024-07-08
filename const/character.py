"""
This module defines constants associated with characters.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Optional, TypeAlias

from const.entity import LivingEntityAttribute

if TYPE_CHECKING:
    CharacterState: TypeAlias = None


class CharacterType(Enum):
    MELEE = auto()
    RANGER = auto()
    SNIPER = auto()


@dataclass(kw_only=True)
class CharacterAttribute(LivingEntityAttribute):
    speed: float
    ability_cd: float | None
    ability_variables: Optional[Any]


MELEE_ATTRIBUTE = CharacterAttribute(
    speed=1,
    attack_range=10,
    attack_damage=3,
    max_health=500,
    vision=15,
    ability_cd=1.5,
    attack_speed=0.8,
    ability_variables=5
)

RANGER_ATTRIBUTE = CharacterAttribute(
    speed=0.7,
    attack_range=25,
    attack_damage=50,
    max_health=200,
    vision=10,
    ability_cd=1.5,
    attack_speed=1,
    ability_variables=100
)

SNIPER_ATTRIBUTE = CharacterAttribute(
    speed=0.4,
    attack_range=50,
    attack_damage=150,
    max_health=300,
    vision=10,
    ability_cd=1.5,
    attack_speed=0.5,
    ability_variables=None
)
