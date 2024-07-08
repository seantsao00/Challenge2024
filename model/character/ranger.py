from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
from event_manager import EventBulletCreate
from instances_manager import get_event_manager, get_model
from model.character import Character
from model.bullet import BulletRanger, BulletCommon

if TYPE_CHECKING:
    from model.team import Team
    from model.entity import Entity


class Ranger(Character):
    """
    Class for the ranger fighter
    Ranger fighter has the following unique moves:
     - area_attack: Attack a locations and damage all nearby foes.
    """

    def __init__(self, position: pg.Vector2 | tuple[float, float], team: Team):
        super().__init__(position, team, const.RANGER_ATTRIBUTE, const.CharacterType.RANGER, None)

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if (self.team != enemy.team
            and dist <= self.attribute.attack_range
            and (now_time - self.attack_time) * self.attribute.attack_speed >= 1):
            bullet = BulletCommon(position=self.position, 
                                  victim=enemy,
                                  team=self.team, 
                                  attacker=self, 
                                  damage=const.RANGER_ATTRIBUTE.attack_damage,
                                  speed=const.BULLET_COMMON_RANGER_SPEED)
            get_event_manager().post(EventBulletCreate(bullet=bullet))
            self.attack_time = now_time

    def ability(self, *args, **kwargs):
        if len(args) < 1 or not isinstance(args[0], pg.Vector2):
            raise ValueError()
        origin: pg.Vector2 = args[0]
        dist = self.position.distance_to(origin)
        if dist <= self.attribute.attack_range:
            print("ranged abilities attack")
            bullet = BulletRanger(position=self.position, 
                                  target=origin,
                                  team=self.team, 
                                  attacker=self)
            get_event_manager().post(EventBulletCreate(bullet=bullet))
        
    def cast_ability(self, *args, **kwargs):
        now_time = get_model().get_time()
        if now_time - self.abilities_time < self.attribute.ability_cd:
            return
        print("cast abilities")
        self.abilities_time = now_time
        self.ability(*args, **kwargs)
