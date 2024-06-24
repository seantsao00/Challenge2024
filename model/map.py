import os 
import csv
import json
from queue import Queue
import random

import pygame as pg

import const 
import util

class Map:
    def __init__(
        self,
        name: str,
        size: tuple[int, int],
        map_list: list[list[int]],
        portals: list[tuple[int, int, int]],
        images: dict[str, int],
        spawn: list[tuple[int]],
        solider_spawn_point,
        map_dir,
        portkey_map,
    ):
        self.name = name
        self.size = size
        self.map = map_list
        self.images = images
        self.portals = portals
        self.spawn = spawn
        self.solider_spawn_point = solider_spawn_point
        self.map_dir = map_dir
        self.connected_component = dict()
        self.closest_cell = dict()
        self.number_of_connected_components = dict()
        self.portkey_map = portkey_map