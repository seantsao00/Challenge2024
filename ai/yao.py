import pygame as pg

from api.prototype import *

class Yao:

    def __init__(self):
        self.api = None

    def run(self, api: API):
        self.api = api
        owned = self.api.get_owned_characters()
        #if self.api.get_current_time() < 10:
        self.api.change_spawn_type(self.api.get_owned_towers()[0], CharacterClass.MELEE)
        self.api.action_wander(self.api.get_owned_characters()[-1])
        victim = None
        for i in api.get_visible_characters():
            if i.team_id != api.get_team_id():
                victim = i
                break
        if victim is not None:
            api.action_move_and_attack(owned, victim)
            api.send_chat("QQhahaha")
        # elif self.api.get_current_time() < 30:
        #     self.api.change_spawn_type(self.api.get_owned_towers()[0], CharacterClass.MELEE)
yao = Yao()

def every_tick(interface: API):
    yao.run(api=interface)
