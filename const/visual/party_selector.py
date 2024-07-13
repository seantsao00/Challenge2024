from __future__ import annotations

import os

from const.team import PartyType
from const.visual import IMAGE_DIR

PARTY_SELECTOR_DIR = 'party_selection/'
PARTY_SELECTOR_BACKGROUND: str = os.path.join(IMAGE_DIR, PARTY_SELECTOR_DIR, 'background.png')
PARTY_SELECTOR_IMAGE: dict[None | PartyType, str] = {
    None: os.path.join(IMAGE_DIR, PARTY_SELECTOR_DIR, 'default.png'),
    PartyType.JUNIOR: os.path.join(IMAGE_DIR, PARTY_SELECTOR_DIR, 'junior.png'),
    PartyType.FBI: os.path.join(IMAGE_DIR, PARTY_SELECTOR_DIR, 'fbi.png'),
    PartyType.POLICE: os.path.join(IMAGE_DIR, PARTY_SELECTOR_DIR, 'police.png'),
    PartyType.BLACK: os.path.join(IMAGE_DIR, PARTY_SELECTOR_DIR, 'black.png'),
    PartyType.MOURI: os.path.join(IMAGE_DIR, PARTY_SELECTOR_DIR, 'mouri.png')
}
