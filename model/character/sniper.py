from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventBulletCreate
from instances_manager import get_event_manager, get_model
from model.bullet import BulletCommon
from model.character import Character
from util import log_info

if TYPE_CHECKING:
    from model.entity import Entity
    from model.team import Team


class Sniper(Character):
    """

    Class for sniper character in the game.
    Sniper has the following unique technique(s):
    focus: Increase damage that can be stacked. Loses stacks when taken damage.
    """

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team):
        super().__init__(position, team, const.SNIPER_ATTRIBUTE,
                         const.CharacterType.SNIPER, const.CharacterState.LEFT)
        self.ability_active = False

    def cast_ability(self, *args, **kwargs):
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.attribute.ability_cd:
            return
        self.abilities_time = now_time
        self.ability()

    def manual_cast_ability(self, *args, **kwargs):
        self.cast_ability(*args, **kwargs)

    def ability(self):
        """Make the bullet become BulletSniper"""
        self.ability_active = True
        log_info("[Sniper] Use ability")

    def record_attack(self, damage: float):
        self.attack_total += damage
        if not self.ascended and self.attack_total >= self.attribute.ascend_threshold:
            self.ascended = True
            if self.state is const.CharacterState.LEFT:
                self.state = const.CharacterState.LEFT_ASCENDED
            elif self.state is const.CharacterState.RIGHT:
                self.state = const.CharacterState.RIGHT_ASCENDED

    def attack(self, enemy: Entity):

        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team
            and dist <= self.attribute.attack_range
                and (now_time - self._last_attack_time) * self.attribute.attack_speed >= 1):
            if not self.ability_active:
                bullet = BulletCommon(position=self.position,
                                      victim=enemy,
                                      team=self.team,
                                      attacker=self,
                                      damage=const.SNIPER_ATTRIBUTE.attack_damage,
                                      speed=const.BULLET_COMMON_SPEED)
            else:
                bullet = BulletCommon(position=self.position,
                                      victim=enemy,
                                      team=self.team,
                                      attacker=self,
                                      damage=const.SNIPER_ATTRIBUTE.ability_variables,
                                      speed=const.BULLET_SNIPER_SPEED)
                self.ability_active = False
            get_event_manager().post(EventBulletCreate(bullet=bullet))
            self._last_attack_time = now_time
