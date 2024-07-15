import math
import random

import pygame as pg

from api.prototype import *


def every_tick(interface: API):
    # 創造空的列表(list)，儲存所有視野可及的敵方士兵
    visible = [] 
    for character in interface.get_visible_characters():
        if character.team_id != interface.get_team_id():
            visible.append(character) 

    # 讓己方隊伍所有的士兵繞著圓圈移動
    interface.action_move_along(interface.get_owned_characters()[:1],
                                pg.Vector2(2 * math.cos(interface.get_current_time() / 20),
                                           2 * math.sin(interface.get_current_time() / 20)))
    # 將所有己方隊伍的士兵移動到列表內的第一個敵方士兵，並統一攻擊它
    if len(visible):
        interface.action_move_to(interface.get_owned_characters()[1:], visible[0].position)
        interface.action_attack(interface.get_owned_characters()[1:], visible[0])
