"""
This module defines constants associated with music.
"""

import os.path

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
