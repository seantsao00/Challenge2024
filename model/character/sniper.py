from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from model.character import Character
from event_manager import EventBulletCreate
from instances_manager import get_event_manager, get_model
from model.bullet import BulletSniper

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
        self.defense = 0
        self.ability_stack = 0

    def ability(self, *args, **kwargs):
        self.ability_stack = 1
    
    def attack(self, enemy: Entity):

        if self.ability_stack > 0:
            self.attribute.attack_damage *= 2
            print("sniper use ability")

        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team
            and dist <= self.attribute.attack_range
                and (now_time - self.attack_time) * self.attribute.attack_speed >= 1):
            bullet = BulletSniper(position=self.position, victim=enemy, team=self.team, attacker=self)
            get_event_manager().post(EventBulletCreate(bullet=bullet))
            self.attack_time = now_time

        if self.ability_stack > 0:
            self.attribute.attack_damage /= 2
            self.ability_stack -= 1
