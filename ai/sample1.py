import math
import random

import pygame as pg

from api.prototype import *


def every_tick(api: API):
    """
    一定要被實作的 function ，會定期被遊戲 call
    在使用 VS Code 寫 code 的時候可以把滑鼠移到變數、函數上方，看它們的詳細解說。
    在使用 VS Code 寫 code 的時候可以按住 Ctrl 再用滑鼠點擊變數、函數，來跳轉到與它們相關的地方。
    在測試的時候可以只放一隻 ai 、在執行時一次加很多 arguments (如 -qrp)。
    """
    # 創造空的列表(list)，儲存所有視野可及的敵方士兵
    visible = []
    for character in api.get_visible_characters():
        if character.team_id != api.get_team_id():
            visible.append(character)

    # 讓己方隊伍所有的士兵繞著圓圈移動
    api.action_move_along(api.get_owned_characters()[:1],
                                pg.Vector2(2 * math.cos(api.get_current_time() / 20),
                                           2 * math.sin(api.get_current_time() / 20)))
    # 將所有己方隊伍的士兵移動到列表內的第一個敵方士兵，並統一攻擊它
    if len(visible):  # 若視野內存在敵方士兵
        api.action_move_to(api.get_owned_characters()[1:], visible[0].position)
        api.action_attack(api.get_owned_characters()[1:], visible[0])
