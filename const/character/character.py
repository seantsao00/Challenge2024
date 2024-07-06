"""
This module defines constants associated with characters.
"""

from dataclasses import dataclass
from enum import Enum, auto


class CharacterType(Enum):
    MELEE = auto()
    RANGER = auto()
    SNIPER = auto()


@dataclass(kw_only=True)
class CharacterAttribute:
    speed: float
    attack_range: float
    damage: float
    max_health: float
    vision: float
    ability_variable: float
    ability_cd: float | None
    attack_speed: float
