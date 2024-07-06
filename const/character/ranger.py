"""
This module defines constants associated with range fighter.
"""
from const.character.character import CharacterAttribute

RANGER_ATTRIBUTE = CharacterAttribute(
    speed=2,
    attack_range=25,
    damage=50,
    health=200,
    vision=30,
    ability_variable=100,
    ability_cd=1.5,
    attack_speed=1
)
