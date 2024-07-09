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
    speed=15,
    attack_range=5,
    attack_damage=45,
    max_health=600,
    vision=20,
    ability_cd=3,
    attack_speed=0.8,
    ability_variables=3
    # damage per second = 36
)

RANGER_ATTRIBUTE = CharacterAttribute(
    speed=10,
    attack_range=20,
    attack_damage=60,
    max_health=300,
    vision=15,
    ability_cd=2,
    attack_speed=1.2,
    ability_variables=30
    # damage per second = 72
)

SNIPER_ATTRIBUTE = CharacterAttribute(
    speed=5,
    attack_range=40,
    attack_damage=300,
    max_health=100,
    vision=0,
    ability_cd=4,
    attack_speed=0.5,
    ability_variables=None
    # damage per second = 150
)

"""
                MELEE vs. RANGER
no ability      8.333     8.333
use ability     8.333     10.8333
need walk       11.333    8.333
need walk use   11.333    10.8333

                MELEE vs. SNIPER
no ability      2.7778    4
use ability     2.7778    8
need walk       6.2778    4
need walk use   6.2778    8


                RANGER vs. SNIPER
no ability      1.39       2
use ability     1.39       2
need walk       3.39       2
need walk use   3.39       2
"""
