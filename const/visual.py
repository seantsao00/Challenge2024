from __future__ import annotations

import os
from typing import TYPE_CHECKING

from const.character import CharacterType
from const.team import PartyType
from const.tower import TowerType

if TYPE_CHECKING:
    from const.entity import EntityState, EntityType

ATTACK_RANGE_COLOR = 'red'
VIEW_RANGE_COLOR = 'blue'
CD_BAR_COLOR = 'blue'

HEALTH_BAR_UPPER = 7
CD_BAR_UPPER = 5

VIEW_EVERYTHING = 0

REGULAR_FONT = './font/Cubic_11_1.300_R.ttf'

IMAGE_DIR = 'image/'

PARTY_PATH: dict[PartyType, str] = {
    PartyType.NEUTRAL: 'entity/neutral/',
    PartyType.JUNIOR: 'entity/junior/',
    PartyType.FBI: 'entity/fbi/',
    PartyType.POLICE: 'entity/police/',
    PartyType.BLACK: 'entity/black/',
    PartyType.MOURI: 'entity/mouri/'
}

TOWER_DIR = 'tower/'
TOWER_IMAGE: dict[TowerType, str] = {
    TowerType.FOUNTAIN: 'fountain.png',
    TowerType.HOTEL: 'neutral_hotel.png',
    TowerType.FERRIS_WHEEL: 'neutral_ferris_wheel.png',
    TowerType.PYLON: 'neutral_pylon.png'
}

CHARACTER_DIR = 'character'
CHARACTER_IMAGE: dict[CharacterType, str] = {
    CharacterType.MELEE: 'melee.png',
    CharacterType.RANGER: 'ranger.png',
    CharacterType.SNIPER: 'sniper.png'
}

ENTITY_IMAGE: dict[PartyType, dict[EntityType, dict[EntityState, str]]] = {
    party: (
        {
            tower: {
                None: os.path.join(IMAGE_DIR, PARTY_PATH[party], TOWER_DIR, TOWER_IMAGE[tower])
            } for tower in TowerType if tower is not TowerType.FOUNTAIN
        } if party is PartyType.NEUTRAL else {
            **{
                character: {
                    None: os.path.join(IMAGE_DIR, PARTY_PATH[party], CHARACTER_DIR, CHARACTER_IMAGE[character])
                } for character in CharacterType
            },
            **{
                tower: {
                    None: os.path.join(IMAGE_DIR, PARTY_PATH[party], TOWER_DIR, TOWER_IMAGE[tower])
                } for tower in TowerType
            }
        }
    ) for party in PartyType
}
"""
structure: ENTITY_IMAGE[party][entity][state]
"""

ENTITY_SIZE: dict[EntityType, dict[EntityState, int]] = {
    **{character: {
        None: 6.25
    } for character in CharacterType},
    **{tower: {
        None: 6.25
    } for tower in TowerType}
}
"""
structure: ENTITY_SIZE[entity][state]
"""
