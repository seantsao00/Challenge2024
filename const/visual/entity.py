from __future__ import annotations

import os
from enum import Enum, auto
from typing import TYPE_CHECKING

import pygame as pg

from const.bullet import BulletType
from const.character import AscendanceType, CharacterState, CharacterType
from const.team import PartyType
from const.tower import TowerType
from const.vehicle import VehicleState, VehicleType
from const.visual import IMAGE_DIR

if TYPE_CHECKING:
    from const.entity import EntityState, EntityType

ATTACK_RANGE_COLOR = 'red'
VIEW_RANGE_COLOR = 'blue'
CD_BAR_COLOR = 'blue'
# open for color recommandation
# HEALTH_BAR_COLOR = ['yellow', 'paleturquoise2', 'orange', 'violet']
# HEALTH_BAR_COLOR = [(255, 255, 0), (175, 238, 238), (255, 165, 0), (238, 130, 238)]
HEALTH_BAR_COLOR = [(255, 255, 0), (175, 238, 238), (255, 128, 0), (204, 0, 204)]

HEALTH_BAR_UPPER = pg.Vector2(0, -6)
CD_BAR_UPPER = pg.Vector2(0, -4)
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
CHARACTER_IMAGE: dict[(CharacterType, CharacterState), str] = {
    (CharacterType.MELEE, CharacterState.LEFT): 'melee_left.png',
    (CharacterType.RANGER, CharacterState.LEFT): 'ranger_left.png',
    (CharacterType.SNIPER, CharacterState.LEFT): 'sniper_left.png',
    (CharacterType.MELEE, CharacterState.RIGHT): 'melee_right.png',
    (CharacterType.RANGER, CharacterState.RIGHT): 'ranger_right.png',
    (CharacterType.SNIPER, CharacterState.RIGHT): 'sniper_right.png',
}
CHARACTER_ASCENDED_ARMOR_IMAGE: dict[(CharacterType, CharacterState), str] = {
    (CharacterType.MELEE, CharacterState.LEFT): 'melee_ascended_left.png',
    (CharacterType.RANGER, CharacterState.LEFT): 'ranger_ascended_left.png',
    (CharacterType.SNIPER, CharacterState.LEFT): 'sniper_ascended_left.png',
    (CharacterType.MELEE, CharacterState.RIGHT): 'melee_ascended_right.png',
    (CharacterType.RANGER, CharacterState.RIGHT): 'ranger_ascended_right.png',
    (CharacterType.SNIPER, CharacterState.RIGHT): 'sniper_ascended_right.png',
}
CHARACTER_ASCENDED_CROWN_IMAGE: dict[CharacterType, str] = {
    CharacterType.MELEE: 'melee_crown.png',
    CharacterType.RANGER: 'ranger_crown.png',
    CharacterType.SNIPER: 'sniper_crown.png',
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

VEHICLE_DIR = 'vehicle/'
VEHICLE_IMAGE: dict[VehicleState, str] = {
    VehicleState.BACK: 'back.png',
    VehicleState.FRONT: 'front.png',
    VehicleState.LEFT: 'left.png',
    VehicleState.RIGHT: 'right.png'
}

ASCENDANCE_DIR = 'ascendance/'
ASCENDANCE_IMAGE: dict[PartyType, dict[AscendanceType, dict[CharacterType, dict[CharacterState, str]]]] = {
    party: (
        {
            character: {
                state: {
                    AscendanceType.ARMOR: os.path.join(
                        IMAGE_DIR, PARTY_PATH[party], ASCENDANCE_DIR, CHARACTER_ASCENDED_ARMOR_IMAGE[(
                            character, state)]
                    ),
                    AscendanceType.CROWN: os.path.join(
                        IMAGE_DIR, PARTY_PATH[party], ASCENDANCE_DIR, CHARACTER_ASCENDED_CROWN_IMAGE[character]
                    )
                } for state in CharacterState
            } for character in CharacterType
        }
    ) for party in PartyType if party is not PartyType.NEUTRAL
}
"""
structure: ASCENDANCE_IMAGE[party][character][state][ascendance]
"""

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
            },
            **{
                vehicle: {
                    state: os.path.join(IMAGE_DIR, PARTY_PATH[party], VEHICLE_DIR, VEHICLE_IMAGE[state]) for state in VehicleState
                } for vehicle in VehicleType
            }
        } if party is PartyType.NEUTRAL else {
            **{
                character: {
                    state: os.path.join(
                        IMAGE_DIR, PARTY_PATH[party], CHARACTER_DIR, CHARACTER_IMAGE[(character, state)]) for state in CharacterState
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
ENTITY_SIZE: dict[EntityType, dict[EntityState, tuple[float, float]]] = {
    **{character: {
        state: (9, 13.2) for state in CharacterState
    } for character in CharacterType},
    **{tower: {
        None: (20, 12)
    } for tower in TowerType},
    **{bullet: {
        None: (4, 4),
    } for bullet in BulletType},
    **{vehicle: {
        state: (9, 13.2) for state in VehicleState
    } for vehicle in VehicleType},
}
"""
structure: ENTITY_SIZE[entity][state]
"""
# Size for clicking
CLICK_SIZE: dict[EntityType, dict[EntityState, int]] = {
    **{character: {
        state: 6.25 for state in CharacterState
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

PATH_WIDTH = 6
DESTINATION_RADIUS = 8
