"""
This module defines constants associated with music.
"""

from const.team import PartyType

MUSIC_DIR = "music/"

MUSIC_PATH: dict[PartyType, str] = {
    PartyType.NEUTRAL: 'demo.mp3',
    PartyType.JUNIOR: 'bgmjunior.mp3',
    PartyType.FBI: 'bgmfbi.mp3',
    PartyType.POLICE: 'bgmpolice.mp3',
    PartyType.BLACK: 'bgmblack.mp3',
    PartyType.MOURI: 'bgmmouri.mp3'
}
