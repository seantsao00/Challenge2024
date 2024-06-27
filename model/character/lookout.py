import const
from event_manager import EventAttack
from model.character import Character


class Lookout(Character):
    """

    Class for lookout character in the game.
    Lookout has the following unique technique(s):
    focus: Increase damage that can be stacked. Loses stacks when taken damage.
    """

    def __init__(self, team, position, alive=True):
        super().__init__(team, position, const.LOOKOUT_SPEED, const.LOOKOUT_ATTACK_RANGE,
                         const.LOOKOUT_DAMAGE, const.LOOKOUT_HEALTH, const.LOOKOUT_VISION, alive)

    def focus(self):
        self.damage += 5

    def take_damage(self, event: EventAttack):
        self.damage = const.LOOKOUT_DAMAGE
        super().take_damage(event)
