import const
from event_manager import EventAttack, EventBulletCreate, EventMultiAttack
from instances_manager import get_event_manager, get_model
from model.bullet import BulletRanger, BulletSniper
from model.character import Character
from model.entity import Entity


class Sniper(Character):
    """

    Class for sniper character in the game.
    Sniper has the following unique technique(s):
    focus: Increase damage that can be stacked. Loses stacks when taken damage.
    """

    def __init__(self, team, position, ability=0):
        super().__init__(position, team, const.SNIPER_SPEED, const.SNIPER_ATTACK_RANGE,
                         const.SNIPER_DAMAGE, const.SNIPER_HEALTH, const.SNIPER_VISION, const.SNIPER_ATTACK_SPEED, const.SNIPER_ABILITIES_CD, 'sniper')
        self.ability = ability
        self.imgstate = 'sniper'

    def attack(self, enemy: Entity):
        now_time = get_model().get_time()
        dist = self.position.distance_to(enemy.position)
        if self.team != enemy.team and dist <= self.attack_range and (now_time - self.attack_time) * self.attack_speed >= 1:
            bullet = BulletSniper(position=self.position, victim=enemy)
            get_event_manager().post(EventBulletCreate(bullet=bullet), self.team.id)
            self.attack_time = now_time

    def abilities(self):
        self.ability = 1

    def attack(self, enemy: Entity):
        if self.ability > 0:
            self.damage *= 2
        super().attack(enemy)
        if self.ability > 0:
            self.damage /= 2
            self.ability -= 1
