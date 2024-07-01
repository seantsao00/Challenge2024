import pygame as pg

import view
from model.entity import Entity


class PauseMenu:
    def __init__(self):
        self.enabled: bool = False
        self.options = ['Resume', 'Restart', 'Exit']
        self.selected = 0
        
    def change_selected(self, move):
        self.selected += move
        if self.selected == 3:
            self.selected = 0
        elif self.selected == -1:
            self.selected = 2

    def enable_menu(self):
        self.enabled = True
    
    def disable_menu(self):
        self.enabled = False