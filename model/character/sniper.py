import const
from event_manager import EventAttack
from model.character import Character


class Sniper(Character):
    """

    Class for sniper character in the game.
    Sniper has the following unique technique(s):
    focus: Increase damage that can be stacked. Loses stacks when taken damage.
    """

    def __init__(self, team, position):
        super().__init__(position, team, const.SNIPER_SPEED, const.SNIPER_ATTACK_RANGE,
                         const.SNIPER_DAMAGE, const.SNIPER_HEALTH, const.SNIPER_VISION, const.SNIPER_CDTIME, const.SNIPER_ABILITIES_CD)

    def abilities(self):
        self.damage += 5

    def take_damage(self, event: EventAttack):
        self.damage = const.SNIPER_DAMAGE
        super().take_damage(event)
