import pygame as pg

import const
import model

class RangeView:
    def __init__(self, character: 'model.Entity'):
        self.character = character
        self.radius: float = None
        self.color = None
    
    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.character.position, self.radius, width=1)


class AttackRangeView(RangeView):
    def __init__(self, character: 'model.Entity'):
        super().__init__(character)
        self.color = const.ATTACK_RANGE_COLOR
        self.radius = self.character.attack_range - 0.5

class ViewRangeView(RangeView):
    def __init__(self, character: 'model.Entity'):
        super().__init__(character)
        self.color = const.VIEW_RANGE_COLOR
        self.radius = self.character.vision + 0.5