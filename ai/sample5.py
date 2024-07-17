"""
在寫 ai 的時候可以把不同的邏輯分給不同的人寫，寫成數個 functions ，增加寫的效率。
可以按 Ctrl + 變數或函式快速跳轉。
"""
import math
import random

import pygame as pg

from api.prototype import *

siege_targets: list[Character | Tower] = []
"""圍毆的目標"""


def chat(api: API) -> None:
    """很長的 function 可以按 function 左側的箭頭把 function 給「收起來」。"""
    lyrics = {18: "We're no strangers to love", 22: "You know the rules and so do I", 26: "A full commitment's what I'm thinking of", 30: "You wouldn't get this from any other guy", 34: "I just want to tell you how I'm feeling", 39: "Gotta make you understand", 43: "Never gonna give you up, never gonna let you down", 47: "Never gonna run around and desert you", 51: "Never gonna make you cry, never gonna say goodbye", 55: "Never gonna tell a lie and hurt you", 60: "We've known each other for so long", 64: "Your heart's been aching but you're too shy to say it", 69: "Inside we both know what's been going on", 73: "We know the game and we're gonna play it", 77: "And if you ask me how I'm feeling", 82: "Don't tell me you're too blind to see", 85: "Never gonna give you up, never gonna let you down", 89: "Never gonna run around and desert you", 93: "Never gonna make you cry, never gonna say goodbye", 97: "Never gonna tell a lie and hurt you", 102: "Never gonna give you up, never gonna let you down", 106: "Never gonna run around and desert you", 110: "Never gonna make you cry, never gonna say goodbye", 115: "Never gonna tell a lie and hurt you",
              119: "(Ooh give you up)", 124: "(Ooh give you up)", 128: "(Ooh) Never gonna give, never gonna give (give you up)", 132: "(Ooh) Never gonna give, never gonna give (give you up)", 136: "We've known each other for so long", 140: "Your heart's been aching but you're too shy to say it", 145: "Inside we both know what's been going on", 149: "We know the game and we're gonna play it", 153: "I just want to tell you how I'm feeling", 158: "Gotta make you understand", 161: "Never gonna give you up, never gonna let you down", 165: "Never gonna run around and desert you", 169: "Never gonna make you cry, never gonna say goodbye", 173: "Never gonna tell a lie and hurt you", 178: "Never gonna give you up, never gonna let you down", 182: "Never gonna run around and desert you", 186: "Never gonna make you cry, never gonna say goodbye", 191: "Never gonna tell a lie and hurt you", 195: "Never gonna give you up, never gonna let you down", 199: "Never gonna run around and desert you", 203: "Never gonna make you cry, never gonna say goodbye", 208: "Never gonna tell a lie and hurt you", 213: "www.RentAnAdviser.com"}
    time_now = api.get_current_time()
    if time_now in lyrics:
        api.send_chat(lyrics[time_now])


def calculate_distance(a: pg.Vector2, b: pg.Vector2) -> float:
    """計算兩點之間的距離(可以用向量減法理解)"""
    return (a-b).length()


def get_visible_enemies(api: API) -> tuple[list[Tower], list[Character]]:
    """找出視野範圍內的可攻擊目標。"""
    my_team_id = api.get_team_id()

    visible_enemy_towers = []
    visible_towers = api.get_visible_towers()
    for tower in visible_towers:
        if tower.team_id != my_team_id:
            visible_enemy_towers.append(tower)

    visible_enemy_characters = []
    visible_characters = api.get_visible_characters()
    for character in visible_characters:
        if character.team_id != my_team_id:
            visible_enemy_characters.append(character)

    return (visible_enemy_towers, visible_enemy_characters)


def get_nearby_fellows(api: API, position: pg.Vector2, distance: int = 40) -> list[Character]:
    """
    拿到距離某點附近(距離 distance 內)友軍的 list，如果沒有特別指定 distance 的話預設是 40。
    """
    my_character = api.get_owned_characters()
    nearby_fellows = []
    for character in my_character:
        if calculate_distance(character.position, position) <= distance:
            nearby_fellows.append(character)
    return nearby_fellows

def get_nearest_friend_melee(api: API, position: pg.Vector2) -> Character | None:
    """拿到最近的友方進戰士兵，如果完全沒有的話就回傳 None"""
    my_characters = api.get_owned_characters()
    my_melee = []
    for character in my_characters:
        if character.type is CharacterClass.MELEE:
            my_melee.append(character)
    if len(my_melee) == 0:
        return None
    my_melee = api.sort_by_distance(my_melee, position)
    return my_melee[0]

def melee_action(api: API, melee: Character) -> None:
    """
    決定近戰兵現在要幹嘛
    """
    assert melee.type is CharacterClass.MELEE, 'This function is for melee'
    # 這行 assert 會確保傳進來的 character 是近戰，不然就噴出逗號後面的錯誤
    api.action_cast_ability(melee)
    # melee 的技能開了不虧

    if len(siege_targets) != 0:
        nearest_siege_target = api.sort_by_distance(siege_targets, melee.position)[0]
        # sort_by_distance 後第 0 個，也就是離自己最近的圍毆目標
        if calculate_distance(melee.position, nearest_siege_target.position) < 50:
            # 圍毆目標離自己夠近就衝過去打
            api.action_move_to(melee, nearest_siege_target.position)
            api.action_attack(melee, nearest_siege_target)

    enemies = get_visible_enemies(api)
    for enemy_tower in enemies[0]:
        if enemy_tower.is_fountain:
            # 如果這是敵方的主堡就忽略，因為不能攻擊
            pass
        else:
            if calculate_distance(melee.position, enemy_tower.position) <= enemy_tower.attack_range + 5:
                # 已經離塔的攻擊距離很近或已經在裡面
                nearby_fellows = get_nearby_fellows(api, melee.position)
                if len(nearby_fellows) > 10:
                    # 周圍有很多友軍的話就叫大家一起上
                    siege_targets.append(enemy_tower)
    for enemy_character in enemies[1]:
        if calculate_distance(melee.position, enemy_character.position) <= enemy_character.attack_range + 5:
            # 已經離敵方的攻擊距離很近或已經在裡面
            nearby_fellows = get_nearby_fellows(api, melee.position)
            if len(nearby_fellows) > 10:
                # 周圍有很多友軍的話就叫大家一起上
                siege_targets.append(enemy_character)
    api.action_wander(melee)
    # 叫近戰兵亂走去探視野


def ranger_action(api: API, ranger: Character):
    """決定遠程兵要做什麼"""
    assert ranger.type is CharacterClass.RANGER, 'This function is for ranger'
    # 這行 assert 會確保傳進來的 character 是遠程，不然就噴出逗號後面的錯誤
    random_displacement = pg.Vector2()
    random_displacement.from_polar(
        (random.uniform(0, ranger.attack_range), random.uniform(0, 360)))
    api.action_cast_ability(ranger, position=ranger.position+random_displacement)
    # 隨便在 ranger 周圍的某個點放煙火(技能)

    if len(siege_targets) != 0:
        nearest_siege_target = api.sort_by_distance(siege_targets, ranger.position)[0]
        # sort_by_distance 後第 0 個，也就是離自己最近的圍毆目標
        api.action_move_to(ranger, nearest_siege_target.position)
        api.action_attack(ranger, nearest_siege_target)
        # 直接去打最近的圍毆目標

    nearest_friend_melee = get_nearest_friend_melee(api, ranger.position)
    if nearest_friend_melee is not None:
        api.action_move_to(ranger, get_nearest_friend_melee(api, ranger.position).position)
        # 跟著離自己最近的進戰走


def sniper_action(api: API, sniper: Character):
    """決定狙擊手要做什麼"""
    assert sniper.type is CharacterClass.SNIPER, 'This function is for sniper'
    # 這行 assert 會確保傳進來的 character 是狙擊手，不然就噴出逗號後面的錯誤
    api.action_cast_ability(sniper)
    # sniper 的技能開了不虧

    if len(siege_targets) != 0:
        nearest_siege_target = api.sort_by_distance(siege_targets, sniper.position)[0]
        # sort_by_distance 後第 0 個，也就是離自己最近的圍毆目標
        api.action_move_to(sniper, nearest_siege_target.position)
        api.action_attack(sniper, nearest_siege_target)
        # 直接去打最近的圍毆目標

    nearest_friend_melee = get_nearest_friend_melee(api, sniper.position)
    if nearest_friend_melee is not None:
        api.action_move_to(sniper, get_nearest_friend_melee(api, sniper.position).position)
        # 跟著離自己最近的進戰走

def every_tick(api: API):
    """
    一定要被實作的 function ，會定期被遊戲 call
    在使用 VS Code 寫 code 的時候可以把滑鼠移到變數、函數上方，看它們的詳細解說。
    在使用 VS Code 寫 code 的時候可以按住 Ctrl 再用滑鼠點擊變數、函數，來跳轉到與它們相關的地方。
    在測試的時候可以只放一隻 ai 、在執行時一次加很多 arguments (如 -qrp)。
    """
    my_towers = api.get_owned_towers()
    for tower in my_towers:
        draw = random.random()
        if draw <= 1/3:
            api.change_spawn_type(tower, CharacterClass.MELEE)
        elif draw <= 2/3:
            api.change_spawn_type(tower, CharacterClass.RANGER)
        else:
            api.change_spawn_type(tower, CharacterClass.SNIPER)
        # 隨機塔所生的兵種

    my_characters = api.get_owned_characters()
    for character in my_characters:
        if character.type is CharacterClass.MELEE:
            melee_action(api, character)
        if character.type is CharacterClass.RANGER:
            ranger_action(api, character)
        if character.type is CharacterClass.SNIPER:
            sniper_action(api, character)
    chat(api)
