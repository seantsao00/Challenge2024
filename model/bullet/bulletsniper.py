from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from instances_manager import get_event_manager, get_model

if TYPE_CHECKING:
    from model.team import Team
    from model.entity import LivingEntity

from model.bullet import BulletCommon


class BulletSniper(BulletCommon):
    def __init__(self, position, team, attacker, victim: LivingEntity = None):
        super().__init__(position=position,
                         team=team,
                         speed=const.BULLET_SNIPER_SPEED,
                         attacker=attacker,
                         damage=const.SNIPER_ATTRIBUTE.ability_variables,
                         victim=victim,
                         entity_type=const.BulletType.SNIPER)
