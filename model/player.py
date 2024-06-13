"""
The module defines Player class.
"""

import pygame as pg

from model.entity import Entity
import const


class Player(Entity):
    def __init__(self, player_id: const.PlayerIds):
        self.id = player_id
        self.running = False
        self.position = pg.Vector2(100, 100)
        self.speed = const.PlayerSpeeds.WALK

    def move(self, displacement: pg.Vector2):
        """
        Change the position of object.

        direction need to be a non-zero vector of which length does not matter.
        """
        if displacement.length() == 0:
            raise ValueError(f"move() method of player {self.id} take zero displacement vector.")

        # Limit displacement exceeding player's speed
        if displacement.length() > self.speed:
            displacement = displacement.normalize() * self.speed

        self.position += displacement
