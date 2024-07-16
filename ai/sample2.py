import math
import random

import pygame as pg

from api.prototype import *


def every_tick(api: API):
    # 創造空的列表(list)，儲存所有視野可及的敵方士兵
    visible = [] 
    for character in api.get_visible_characters():
        if character.team_id != api.get_team_id():
            visible.append(character) 

    # 將所有己方隊伍的士兵移動到某個隨機的位置
    api.action_move_to(api.get_owned_characters(), pg.Vector2(random.random() * 250, random.random() * 250))

    # 將所有己方隊伍的士兵移動到列表內的第一個敵方士兵，並統一攻擊它
    if len(visible):
        api.action_move_to(api.get_owned_characters()[1:], visible[0].position)
        api.action_attack(api.get_owned_characters()[1:], visible[0])
