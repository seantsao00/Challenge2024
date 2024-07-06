"""
This module defines constants associated with melee. (Value to be corrected with official version of docs)
"""
from const.character.character import CharacterAttribute

MELEE_ATTRIBUTE = CharacterAttribute(
    speed=2,
    attack_range=10,
    damage=75,
    max_health=500,
    vision=30,
    ability_variable=5,
    ability_cd=1.5,
    attack_speed=0.8
)
