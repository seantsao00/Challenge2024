"""
This module defines constants associated with music.
"""

import os.path
from enum import Enum, auto

from const.team import PartyType

MUSIC_DIR = 'music/'

BGM_DIR = os.path.join(MUSIC_DIR, 'bgm')

BGM_PATH: dict[PartyType, str] = {
    PartyType.NEUTRAL: os.path.join(BGM_DIR, 'title.mp3'),
    PartyType.JUNIOR: os.path.join(BGM_DIR, 'junior.mp3'),
    PartyType.FBI: os.path.join(BGM_DIR, 'fbi.mp3'),
    PartyType.POLICE: os.path.join(BGM_DIR, 'police.mp3'),
    PartyType.BLACK: os.path.join(BGM_DIR, 'black.mp3'),
    PartyType.MOURI: os.path.join(BGM_DIR, 'mouri.mp3')
}

BGM_END_PATH = os.path.join(BGM_DIR, 'end.mp3')

BGM_VOLUME = 0.5

EFFECT_DIR = os.path.join(MUSIC_DIR, 'effect')


class EffectType(Enum):
    """This is for party selection"""
    SELECT = auto()
    ATTACK_MELEE = auto()
    ATTACK_RANGE = auto()


EFFECT_PATH: dict[EffectType, str] = {
    EffectType.SELECT: os.path.join(EFFECT_DIR, 'select.mp3'),
    EffectType.ATTACK_MELEE: os.path.join(EFFECT_DIR, 'attack_melee.mp3'),
    EffectType.ATTACK_RANGE: os.path.join(EFFECT_DIR, 'attack_range.mp3')
}

EFFECT_VOLUME: dict[EffectType, float] = {
    EffectType.SELECT: 0.2,
    EffectType.ATTACK_MELEE: 0.1,
    EffectType.ATTACK_RANGE: 0.1
}
