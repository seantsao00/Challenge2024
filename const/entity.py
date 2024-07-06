"""
This module defines constants associated with entities.
"""
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from character import CharacterType
    from tower import TowerType
    EntityType: TypeAlias = CharacterType | TowerType
    EntityState: TypeAlias = None
