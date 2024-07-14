from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pygame as pg

from const.bullet import BulletType
from const.character import CharacterType
from const.team import PartyType
from const.tower import TowerType
from const.visual import IMAGE_DIR

if TYPE_CHECKING:
    from const.entity import EntityState, EntityType

ATTACK_RANGE_COLOR = 'red'
VIEW_RANGE_COLOR = 'blue'
CD_BAR_COLOR = 'blue'
# open for color recommandation
HEALTH_BAR_COLOR = ['yellow', 'green', 'orange', 'violet', 'red']

HEALTH_BAR_UPPER = 5
CD_BAR_UPPER = 6
TEAM_VISION_BLOCK = 8
VISION_BLOCK_SIZE = 2

VIEW_EVERYTHING = 0

REGULAR_FONT = './font/Cubic_11_1.300_R.ttf'

TOWER_CD_RADIUS = (6, 3.5)
TOWER_CD_COLOR = ('black', CD_BAR_COLOR, 'white')

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

CHARACTER_DIR = 'character/'
CHARACTER_IMAGE: dict[CharacterType, str] = {
    CharacterType.MELEE: 'melee.png',
    CharacterType.RANGER: 'ranger.png',
    CharacterType.SNIPER: 'sniper.png'
}

WEAPON_DIR = 'weapon/'
WEAPON_IMAGE: dict[CharacterType, str] = {
    CharacterType.MELEE: os.path.join(IMAGE_DIR, WEAPON_DIR, 'melee.png'),
    CharacterType.RANGER: os.path.join(IMAGE_DIR, WEAPON_DIR, 'ranger.png'),
    CharacterType.SNIPER: os.path.join(IMAGE_DIR, WEAPON_DIR, 'sniper.png')
}

BULLET_DIR = 'bullet/'
BULLET_IMAGE: dict[BulletType, str] = {
    BulletType.COMMON: 'common.png',
    BulletType.SNIPER: 'sniper.png',
    BulletType.RANGER: 'ranger.png',
}

ENTITY_IMAGE: dict[PartyType, dict[EntityType, dict[EntityState, str]]] = {
    party: (
        {
            **{
                tower: {
                    None: os.path.join(IMAGE_DIR, PARTY_PATH[party], TOWER_DIR, TOWER_IMAGE[tower])
                } for tower in TowerType if tower is not TowerType.FOUNTAIN
            },
            **{
                BulletType.COMMON: {
                    None: os.path.join(
                        IMAGE_DIR, PARTY_PATH[party], BULLET_DIR, BULLET_IMAGE[BulletType.COMMON])
                }
            }
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
            },
            **{
                bullet: {
                    None: os.path.join(IMAGE_DIR, PARTY_PATH[party], BULLET_DIR, BULLET_IMAGE[bullet]),
                } for bullet in BulletType
            }
        }
    ) for party in PartyType
}
"""
structure: ENTITY_IMAGE[party][entity][state]
"""
# Size for showing
ENTITY_SIZE: dict[EntityType, dict[EntityState, int]] = {
    **{character: {
        None: 6.25
    } for character in CharacterType},
    **{tower: {
        None: 10
    } for tower in TowerType},
    **{bullet: {
        None: 2,
    } for bullet in BulletType}
}
"""
structure: ENTITY_SIZE[entity][state]
"""
# Size for clicking
CLICK_SIZE: dict[EntityType, dict[EntityState, int]] = {
    **{character: {
        None: 6.25
    } for character in CharacterType},
    **{tower: {
        None: 20
    } for tower in TowerType},
}
"""
structure: CLICK_SIZE[entity][state]
"""


DRAW_DISPLACEMENT = pg.Vector2(0, -3.125)
DRAW_DISPLACEMENT_Y = -3.125

TRAJECTORY_WIDTH = 6
DESTINATION_RADIUS = 8