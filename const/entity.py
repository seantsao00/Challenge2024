"""
This module defines constants associated with entities.
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from character import CharacterState, CharacterType
    from tower import TowerState, TowerType
    from bullet import BulletState, BulletType
    EntityType: TypeAlias = CharacterType | TowerType | BulletType
    EntityState: TypeAlias = CharacterState | TowerState | BulletState


@dataclass(kw_only=True)
class LivingEntityAttribute:
    attack_damage: float
    attack_speed: float
    attack_range: float
    max_health: float
    vision: float
