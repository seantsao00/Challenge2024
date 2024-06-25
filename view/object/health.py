import pygame as pg

import const
import model
from view.object.object_base import ObjectBase
from util import crop_image

class HealthView:

    def __init__(self, character: 'model.Character'):
        self.max_health = character.health
        self.character = character

    def draw(self, screen: pg.Surface):
        character = self.character
        if character.hidden == True:
            return
        blood_width = (character.health / self.max_health) * const.ENTITY_RADIUS * 2
        pg.draw.rect(screen, (0, 0, 0),
                         (self.character.position.x - const.ENTITY_RADIUS, self.character.position.y - 2 * const.ENTITY_RADIUS - 8, const.ENTITY_RADIUS * 2, 3))
        pg.draw.rect(screen, (255, 0, 0),
                         (self.character.position.x - const.ENTITY_RADIUS, self.character.position.y - 2 * const.ENTITY_RADIUS - 8, blood_width, 3))
        
