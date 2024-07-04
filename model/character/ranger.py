import pygame as pg

import const
from event_manager import EventAttack, EventBulletCreate, EventMultiAttack
from instances_manager import get_event_manager, get_model
from model.bullet import BulletRanger, BulletSniper
from model.character import Character
from model.entity import Entity


class RangerFighter(Character):
    """
    Class for the ranger fighter
    Ranger fighter has the following unique moves:
     - area_attack: Attack a locations and damage all nearby foes.
    """

    def __init__(self, team, position: pg.Vector2):
        super().__init__(position, team, const.RANGER_SPEED, const.RANGER_ATTACK_RANGE,
                         const.RANGER_DAMAGE, const.RANGER_HEALTH, const.RANGER_VISION, const.RANGER_ATTACK_SPEED, const.RANGER_ABILITIES_CD, 'ranger')
        self.abilities_radius = const.RANGER_ABILITIES_RADIUS
        self.imgstate = 'ranger'

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if self.team != enemy.team and dist <= self.attack_range and (now_time - self.attack_time) * self.attack_speed >= 1:
            bullet = BulletSniper(position=self.position, victim=enemy)
            get_event_manager().post(EventBulletCreate(bullet=bullet), self.team.id)
            self.attack_time = now_time

    def abilities(self, *args, **kwargs):
        if len(args) < 1 or not isinstance(args[0], pg.Vector2):
            raise ValueError()
        origin: pg.Vector2 = args[0]
        dist = self.position.distance_to(origin)
        if dist <= self.attack_range:
            print("ranged abilities attack")
            bullet = BulletRanger(position=self.position, target=origin,
                                  radius=self.abilities_radius)
            get_event_manager().post(EventBulletCreate(bullet=bullet), self.team.id)
