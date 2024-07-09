from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from model.character.character import Character
from util import log_info

if TYPE_CHECKING:
    from model.team import Team


class Sniper(Character):
    """

    Class for sniper character in the game.
    Sniper has the following unique technique(s):
    focus: Increase damage that can be stacked. Loses stacks when taken damage.
    """

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team):
        super().__init__(position, team, const.SNIPER_ATTRIBUTE, const.CharacterType.SNIPER, None)

    def ability(self, *args, **kwargs):
        log_info("sniper use ability")
