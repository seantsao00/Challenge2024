import os

import pygame as pg

import const
from event_manager.events import *
from instances_manager import get_event_manager

class BackgroundMusic:
    def __init__(self):
        """
        This function is called when the BackGroundMusic is created to play 
        the background music.
        """
        pg.mixer.init()
        pg.mixer.music.load(os.path.join(const.MUSIC_PATH, "demo.mp3"))
        pg.mixer.music.play(-1)
