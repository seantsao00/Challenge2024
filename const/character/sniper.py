"""
This module defines constants associated with range fighter.
"""
from const.character.character import CharacterAttribute

SNIPER_ATTRIBUTE = CharacterAttribute(
    speed=1.5,
    attack_range=50,
    damage=150,
    health=300,
    vision=50,
    ability_variable=None,
    ability_cd=1.5,
    attack_speed=0.5
)
