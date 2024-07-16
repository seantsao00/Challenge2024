"""
This module defines constants associated with characters.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from const.entity import LivingEntityAttribute

MAX_WANDERING = 50
# Maximum for random in wandering


class CharacterType(Enum):
    MELEE = auto()
    RANGER = auto()
    SNIPER = auto()


class AscendanceType(Enum):
    ARMOR = auto()
    CROWN = auto()


@dataclass(kw_only=True)
class CharacterAttribute(LivingEntityAttribute):
    speed: float
    ability_cd: float | None
    ability_variables: Any | None
    crown_ascendance_threshold: float


class CharacterState(Enum):
    LEFT = auto()
    RIGHT = auto()


MELEE_ATTRIBUTE = CharacterAttribute(
    speed=15,
    attack_range=10,
    attack_damage=36,
    max_health=620,
    vision=20,
    ability_cd=3,
    attack_speed=1,
    ability_variables=3,
    crown_ascendance_threshold=0
    # damage per second = 36
)

RANGER_ATTRIBUTE = CharacterAttribute(
    speed=10,
    attack_range=25,
    attack_damage=60,
    max_health=300,
    vision=15,
    ability_cd=2,
    attack_speed=1.2,
    ability_variables=[15, 60],  # [range, damage] of ability
    crown_ascendance_threshold=1440
    # damage per second = 72
)

SNIPER_ATTRIBUTE = CharacterAttribute(
    speed=5,
    attack_range=40,
    attack_damage=300,
    max_health=100,
    vision=4,
    ability_cd=4,
    attack_speed=0.5,
    ability_variables=300,  # damage of ability
    crown_ascendance_threshold=3000
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

PUDDLE_SPEED_RATIO = 0.5
