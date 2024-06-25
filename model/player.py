"""
The module defines Player class.
"""

import pygame as pg

import const
import view
from model.entity import Entity


class Player(Entity):
    """
    Inherited from `Entity`.
    `pid`: original player ID. Used to prevent conflict from Entity `id`.
    """

    def __init__(self, player_id: const.PlayerIds):
        super().__init__((100, 100))
        self.pid = player_id
        self.running = False
        self.speed = const.PlayerSpeeds.WALK
        self.view = view.PlayerView(self)

    def move(self, displacement: pg.Vector2, dt: float):
        """
        Change the position of object.

        direction need to be a non-zero vector of which length does not matter.
        """
        if displacement.length() == 0:
            raise ValueError(f"move() method of player {self.pid} take zero displacement vector.")

        # Limit displacement exceeding player's speed
        if displacement.length() > self.speed:
            displacement = displacement.normalize() * self.speed * dt

        self.position += displacement
