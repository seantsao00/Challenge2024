"""
The module defines Player class.
"""
import pygame as pg

import const


class Player:
    def __init__(self, player_id: const.PlayerIds):
        self.id = player_id
        self.running = False
        self.position = pg.Vector2(100, 100)
