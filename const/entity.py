"""
This module defines constants associated with entities.
"""
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from character import CharacterState, CharacterType
    from tower import TowerState, TowerType
    EntityType: TypeAlias = CharacterType | TowerType
    EntityState: TypeAlias = CharacterState | TowerState
