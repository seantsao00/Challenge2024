import pygame as pg

from api.prototype import *

class Yao:

    def __init__(self):
        self.api = None

    def run(self, api: API):
        self.api = api
        if self.api.get_current_time() < 20:
            self.api.change_spawn_type(self.api.get_owned_towers()[0], CharacterClass.MELEE)
            self.api.action_wander(self.api.get_owned_characters())

yao = Yao()

def every_tick(interface: API):
    yao.run(api=interface)
