import pygame as pg
from instances_manager import get_event_manager
from model.character import Character
from event_manager import EventMultiAttack
from const.ranged import RANGED_ATTACK_RANGE, RANGED_DAMAGE, RANGED_HEALTH, RANGED_SPEED, RANGED_VISION

class RangedFighter(Character):
    """
    Class for the ranged fighter
    Ranged fighter has the following unique moves:
     - Group attack: Attack a locations and damage all nearby foes.
     - Pierce attack: Attack in a straight line that pierces enemies. (unimplemented)
     (to be changed)
    """
    def __init__(self, team, position):
        super().__init__(self, team, position, RANGED_SPEED, RANGED_ATTACK_RANGE, RANGED_DAMAGE, RANGED_HEALTH, RANGED_VISION, True)
    
    def Group(self, origin: pg.Vector2, radius):
        dist = self.position.distance_to(origin)
        if(dist <= self.attack_range):
            get_event_manager().post(EventMultiAttack(self, 1, target=origin, radius=radius))

    #def Pierce(self, location: pg.Vector2, orientation):
    #    get_event_manager().post(EventMultiAttack(self, 2, orientation=orientation))