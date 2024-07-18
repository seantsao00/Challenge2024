import pygame as pg

from api.prototype import *

class Yao:

    def __init__(self):
        self.api = None

    def run(self, api: API):
        self.api = api
        owned = self.api.get_owned_characters()
        if self.api.get_current_time() < 10:
            self.api.change_spawn_type(self.api.get_owned_towers()[0], CharacterClass.MELEE)
            self.api.action_wander(self.api.get_owned_characters()[-1])
        elif self.api.get_current_time() < 30:
            self.api.change_spawn_type(self.api.get_owned_towers()[0], CharacterClass.MELEE)
yao = Yao()

def every_tick(interface: API):
    yao.run(api=interface)
