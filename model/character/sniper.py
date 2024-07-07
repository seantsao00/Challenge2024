from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from model.character.character import Character

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
        self.defense = 0

    def ability(self, *args, **kwargs):
        print("sniper use ability")
    def __init__(self, team, position, ability=0):
        super().__init__(position, team, const.SNIPER_SPEED, const.SNIPER_ATTACK_RANGE,
                         const.SNIPER_DAMAGE, const.SNIPER_HEALTH, const.SNIPER_VISION, const.SNIPER_ATTACK_SPEED, const.SNIPER_ABILITIES_CD, 'sniper')
        self.ability = ability
        self.imgstate = 'sniper'

    def abilities(self):
        self.ability = 1

    def attack(self, enemy: Entity):
        if self.ability > 0:
            self.damage *= 2

        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if self.team != enemy.team and dist <= self.attack_range and (now_time - self.attack_time) * self.attack_speed >= 1:
            bullet = BulletSniper(position=self.position, victim=enemy,
                                  damage=const.SNIPER_DAMAGE, team=self.team, attacker=self)
            get_event_manager().post(EventBulletCreate(bullet=bullet))
            self.attack_time = now_time

        if self.ability > 0:
            self.damage /= 2
            self.ability -= 1
