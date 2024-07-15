import math
import random

import pygame as pg

from api.prototype import *


class Information:
    destinations: dict[int, pg.Vector2] = {}
    """
    冒號是 type hint 的意思，只是為了註解這個變數是什麼型別。
    這是一個放 id 會拿到該士兵目前目的地的 dictionary。
    """
    last_time_report: int = math.inf  # 無限
    """上次報時的秒數"""


class Const:
    CHAT_PROBABILITY: float = 0.05
    """隨便說說話的機率"""


def assign_random_destination(character: Character, interface: API):
    """assign 一個還沒有開視野的 random position 給 character 。"""
    new_destination = pg.Vector2(random.uniform(0, interface.get_grid_size() - 1),
                                 random.uniform(0, interface.get_grid_size() - 1))
    i = 0
    while interface.is_visible(new_destination):
        new_destination = pg.Vector2(random.uniform(0, interface.get_grid_size() - 1),
                                     random.uniform(0, interface.get_grid_size() - 1))
        i += 1
        if i == 10: # 最多嘗試 10 次
            break
    Information.destinations[character.id] = new_destination
    interface.action_move_to([character], new_destination)

def enemies_near_tower(tower: Tower, interface: API):
    """傳入一座塔，回傳塔附近所有的敵對單位"""
    visible_enemies = [character for character in interface.get_visible_characters()
                if character.team_id != interface.get_team_id()]
    ret = []
    for enemy in visible_enemies:
        if enemy.position.distance_to(tower.position) <= 20:
            ret.append(enemy)
    return ret

def allies_near_tower(tower: Tower, interface: API):
    """傳入一座塔，回傳塔附近己方隊伍所有的塔"""
    allies = [character for character in interface.get_owned_characters()]
    ret = []
    for ally in allies:
        if ally.position.distance_to(tower.position) <= 20:
            ret.append(ally)
    return ret

def every_tick(interface: API):
    """一定要被實作的 function ，會定期被遊戲 call"""
    my_towers = interface.get_owned_towers()

    for tower in my_towers:
        if tower.spawn_character_type is not CharacterClass.MELEE:
            # 把塔所生的士兵種類改成近戰，因為近戰走得比較快
            interface.change_spawn_type(tower, CharacterClass.MELEE)

    my_characters = interface.get_owned_characters()
    for character in my_characters:  # 用 for 迴圈遍歷所有自己的士兵
        if character.id in Information.destinations:  # 這個士兵曾經被 assign 過要往哪裡走
            # 士兵沒有辦法走到任意的實數座標上，所以如果用註解掉的部分判斷是否到達目的地，會覺得士兵永遠沒有走到
            # if character.position == Information.destinations[character.id]: # 這個士兵已經走到他的目的地
            #     assign_random_destination(character, interface)
            if (character.position - Information.destinations[character.id]).length() < 1:
                print(f'{character.id} 已經夠接近目的地了')
                assign_random_destination(character, interface)
        else:  # 這個士兵未曾被 assign 過要往哪裡走
            assign_random_destination(character, interface)

    current_time = interface.get_current_time()
    if int(current_time) % 30 == 0 and abs(current_time - Information.last_time_report) > 2:
        interface.send_chat(f'剩下 {str(180 - int(current_time))} 秒！')
        Information.last_time_report = int(current_time)

    chat_information = [
        '按 ESC 可以暫停',
        '在執行時加上 -h 可以看到所有參數',
        '在執行時加上 -vv 可以看到一堆資訊',
        '在執行時加上 -vv 用滑鼠點擊遊戲畫面會印出座標',
        '在執行時可以放不到 4 個 team_controls',
        '按 Tab 可以切換視野',
        'function call 要記得加括號',
        'action_move_to 要記得傳入的是陣列',
        '在某些地形上會走得比較慢',
        '可以試著在執行時加上 -rq',
        '可以試著在執行時加上 -vvrq',
        '把滑鼠移到變數/函式上可以看詳細內容',
        '將變數內容 print 出來可以幫助 debug'
    ]
    chat_guide = [
        '可以 google 查 "python random"',
        '可以 google 查 "python 標準函式庫"',
        '不同士兵是不是會互相克制？',
        '遇到 bug 時可以試著把東西 print 出來',
        '可以為不同的地圖做不同的策略',
        '可以為不同的士兵做不同的策略',
        '可以為不同的策略做不同的 function',
        '可以用 class 來存資訊',
        '可以多多寫註解',
        '變數不要亂命名',
        '在寫 code 的時候可以多用 auto complete',
        '狙擊手的攻擊距離很遠！！但是很脆走路很慢提供視野也很短...',
        '近戰兵的移動速度很高血量也很多視野也很廣！！但是攻擊距離太短了打不太到移動目標...',
        '遠程兵的攻擊力很高還自帶範圍傷害技能！！但是太脆了需要有人掩護...',
        '中立塔可以提供視野，額外分數，也可以生成額外的兵力，是個重要戰略目標！！多多圍繞中立塔擬定策略吧！',
        '視野很重要！沒有視野就看不到中立塔，也看不到敵人...(用 api.action_wander 可以讓士兵遊走)',
        '有時，偏門玩法反而有奇效！',
        '多研究 API，每個功能都有它的用處！',
        '善用士兵技能！',
    ]
    chat_other = [
        '只探視野不會贏 QQ',
        '我好喜歡資訊營',
        '加油加油！',
        '最新一集劇場版的結局是...',
        '好餓...想吃宵夜了...',
        '(來自 Challenge 員工的哀號)',
        'Bug 退散！',
        '維護良好素質，從你我做起！',
        '為甚麼 sample 好像有點強 @@'
    ]
    chat_choices = chat_information + chat_guide + chat_other
    # 以 Const.CHAT_PROBABILITY 的機率隨便說說話
    if random.uniform(0, 1) < Const.CHAT_PROBABILITY:
        interface.send_chat(random.choice(chat_choices))
