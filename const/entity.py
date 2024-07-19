"""
This module defines constants associated with entities.
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from const.bullet import BulletState, BulletType
    from const.character import CharacterState, CharacterType
    from const.tower import TowerState, TowerType
    from const.vehicle import VehicleState, VehicleType

    EntityType: TypeAlias = CharacterType | TowerType | BulletType | VehicleType
    EntityState: TypeAlias = CharacterState | TowerState | BulletState | VehicleState


@dataclass(kw_only=True)
class LivingEntityAttribute:
    attack_damage: float
    attack_speed: float
    attack_range: float
    max_health: float
    vision: float
