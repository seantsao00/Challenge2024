import pygame as pg

import const
from model.character.character import Character
from model.entity import Entity


class Sniper(Character):
    """

    Class for sniper character in the game.
    Sniper has the following unique technique(s):
    focus: Increase damage that can be stacked. Loses stacks when taken damage.
    """

    def __init__(self, position: pg.Vector2 | tuple[float, float], party: const.PartyType):
        super().__init__(position, party, const.MELEE_ATTRIBUTE, None)
        self.defense = 0

    def abilities(self):
        print("sniper use abilities")
        self.ability = 1

    def attack(self, enemy: Entity):
        if self.ability > 0:
            self.attack_damage *= 2
        super().attack(enemy)
        if self.ability > 0:
            self.attack_damage /= 2
            self.ability -= 1
