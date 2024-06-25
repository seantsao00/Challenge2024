import pygame as pg
from model.character import Character
from const.lookout import LOOKOUT_ATTACK_RANGE, LOOKOUT_DAMAGE, LOOKOUT_HEALTH, LOOKOUT_SPEED, LOOKOUT_VISION
from event_manager import EventAttack


class Lookout(Character):
    """

    Class for lookout character in the game.
    Lookout has the following unique technique(s):
    focus: Increase damage that can be stacked. Loses stacks when taken damage.
    """

    def __init__(self, team, position, alive=True):
        super().__init__(team, position, LOOKOUT_SPEED, LOOKOUT_ATTACK_RANGE,
                         LOOKOUT_DAMAGE, LOOKOUT_HEALTH, LOOKOUT_VISION, alive)

    def focus(self):
        self.damage += 5

    def take_damage(self, event: EventAttack):
        self.damage = LOOKOUT_DAMAGE
        super().take_damage(event)
