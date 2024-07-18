import math
import random

import pygame as pg

from api.prototype import *

class Haruhikage:
    def __init__(self):
        self.lyrics = [
            [15, "悴んだ心 ふるえる眼差し世界で"],
            [21, "僕は ひとりぼっちだった"],
            [25, "散ることしか知らない春は"],
            [31, "毎年 冷たくあしらう"],
            [37, "暗がりの中 一方通行に ただただ"],
            [44, "言葉を書き殴って 期待するだけ"],
            [48, "むなしいと分かっていても"],
            [55, "救いを求め続けた"],
            [59, "（せつなくて いとおしい）"],
            [63, "今ならば 分かる気がする"],
            [67, "（しあわせで くるおしい）"],
            [70, "あの日泣けなかった僕を"],
            [74, "光は やさしく連れ立つよ"],
            [82, "雲間をぬって きらりきらり"],
            [85, "心満たしては 溢れ"],
            [89, "いつしか頬を きらりきらり"],
            [93, "熱く 熱く濡らしてゆく"],
            [96, "君の手は どうしてこんなにも温かいの？"],
            [103, "ねぇお願い どうかこのまま 離さないでいて"],
            [115, "縁を結んでは ほどきほどかれ"],
            [119, "誰しもがそれを喜び悲しみながら"],
            [127, "愛を数えてゆく"],
            [132, "鼓動を確かめるように"],
            [138, "（うれしくて さびしくて）"],
            [141, "今だから 分かる気がした"],
            [145, "（たいせつで こわくって）"],
            [148, "あの日泣けなかった僕を"],
            [152, "光は やさしく抱きしめた"],
            [175, "照らされた世界 咲き誇る大切な人"],
            [181, "あたたかさを知った春は 僕のため 君のための"],
            [188, "涙を流すよ"],
            [190, "Ah なんて眩しいんだろう"],
            [194, "Ah なんて美しいんだろう"],
            [210, "雲間をぬって きらりきらり"],
            [215, "心満たしては 溢れ"],
            [219, "いつしか頬を きらりきらり"],
            [223, "熱く 熱く濡らしてゆく"],
            [226, "君の手は どうしてこんなにも温かいの？"],
            [234, "ねぇお願い どうかこのまま 離さないでいて"],
            [243, "ずっと ずっと 離さないでいて"]
        ]

    def sing(self, interface: API):
        time = interface.get_current_time()
        if time < 10: 
            interface.send_chat("Haruhikage Loading...")
        elif len(self.lyrics) == 0:
            interface.send_chat("為什麼要演奏春日影!!!")
        elif time > self.lyrics[0][0] * 0.6:
            interface.send_chat(self.lyrics[0][1])
            self.lyrics.pop(0)

    def maneuver(self, interface: API):
        owned_towers = interface.get_owned_towers()
        for tower in owned_towers:
            interface.change_spawn_type(tower, random.choice([CharacterClass.MELEE, CharacterClass.RANGER, CharacterClass.SNIPER]))
        owned_characters = interface.get_owned_characters()
        interface.action_cast_ability(owned_characters)
        for ch in owned_characters:
            if interface.get_movement(ch).status is not MovementStatusClass.WANDERING:
                interface.action_wander([ch])
        visible = [character for character in interface.get_visible_characters()
                if character.team_id != interface.get_team_id()]
        for enemy in visible:
            if enemy.team_id != interface.get_team_id():
                interface.action_attack(owned_characters, enemy)

haruhikage = Haruhikage()

def every_tick(interface: API):
    haruhikage.sing(interface)
    haruhikage.maneuver(interface)

