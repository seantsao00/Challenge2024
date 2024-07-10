from __future__ import annotations

import os

from const.team import PartyType
from const.visual import IMAGE_DIR

PARTY_SELECTION_DIR = 'party_selection/'
PARTY_SELECTION_BACKGROUND: str = os.path.join(IMAGE_DIR, PARTY_SELECTION_DIR, 'background.png')
PARTY_SELECTION_IMAGE: dict[None | PartyType, str] = {
    None: os.path.join(IMAGE_DIR, PARTY_SELECTION_DIR, 'default.png'),
    PartyType.JUNIOR: os.path.join(IMAGE_DIR, PARTY_SELECTION_DIR, 'junior.png'),
    PartyType.FBI: os.path.join(IMAGE_DIR, PARTY_SELECTION_DIR, 'fbi.png'),
    PartyType.POLICE: os.path.join(IMAGE_DIR, PARTY_SELECTION_DIR, 'police.png'),
    PartyType.BLACK: os.path.join(IMAGE_DIR, PARTY_SELECTION_DIR, 'black.png'),
    PartyType.MOURI: os.path.join(IMAGE_DIR, PARTY_SELECTION_DIR, 'mouri.png')
}
