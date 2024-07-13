from __future__ import annotations

from typing import TYPE_CHECKING

import const
from model.bullet.bullet_common import BulletCommon

if TYPE_CHECKING:
    from model.entity import LivingEntity


class BulletSniper(BulletCommon):
    def __init__(self, position, team, attacker, victim: LivingEntity = None):
        super().__init__(position=position,
                         team=team,
                         speed=const.BULLET_SNIPER_SPEED,
                         attacker=attacker,
                         damage=const.SNIPER_ATTRIBUTE.ability_variables,
                         victim=victim,
                         entity_type=const.BulletType.SNIPER)
