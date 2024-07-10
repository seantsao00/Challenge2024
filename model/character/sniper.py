from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from model.character import Character
from util import log_info
from event_manager import EventBulletCreate
from instances_manager import get_event_manager, get_model
from model.bullet import BulletSniper, BulletCommon

if TYPE_CHECKING:
    from model.team import Team
    from model.entity import Entity


class Sniper(Character):
    """

    Class for sniper character in the game.
    Sniper has the following unique technique(s):
    focus: Increase damage that can be stacked. Loses stacks when taken damage.
    """

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team):
        super().__init__(position, team, const.SNIPER_ATTRIBUTE, const.CharacterType.SNIPER, None)
        self.ability_active = False
    
    def cast_ability(self, *args, **kwargs):
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.attribute.ability_cd:
            return
        print("cast abilities")
        self.abilities_time = now_time
        self.ability()

    def ability(self):
        """Make the bullet become BulletSniper"""
        self.ability_active = True
        log_info("sniper use ability")

    def attack(self, enemy: Entity):

        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team
            and dist <= self.attribute.attack_range
            and (now_time - self.attack_time) * self.attribute.attack_speed >= 1):
            if not self.ability_active:
                bullet = BulletCommon(position=self.position, 
                                      victim=enemy,
                                      team=self.team, 
                                      attacker=self, 
                                      damage=const.SNIPER_ATTRIBUTE.attack_damage,
                                      speed=const.BULLET_COMMON_SPEED)
            else:
                bullet = BulletSniper(position=self.position, 
                                      victim=enemy,
                                      team=self.team, 
                                      attacker=self)
                self.ability_active = False
            get_event_manager().post(EventBulletCreate(bullet=bullet))
            self.attack_time = now_time

