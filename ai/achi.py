import random

import pygame as pg

from api.prototype import *

chat_list=['我個人認為義大利麵就應該拌 42 號混泥土',
           '因為這個螺絲釘的長度很容易直接影響到挖掘機的扭矩',
           '你往裡砸的時候一瞬間他就會產生大量的高能蛋白',
           '俗稱 UFO，會嚴重影響經濟的發展',
           '以至於對整個太平洋和充電器的核污染',
           '再或者說，透過這勾股定理',
           '很容易推斷出人工飼養的東條英機',
           '他是可以捕獲野生的三角函數',
           '所以說不管這秦始皇的切面是否具有放射性',
           '川普的 N 次方是否有沈澱物',
           '都不會影響到沃爾瑪跟維爾康在南極匯合']

class Achi:

    def __init__(self):
        self.api = None

    def run(self, api: API):
        self.api = api
        my_tower = self.api.get_owned_towers()
        self.api.change_spawn_type(my_tower[0], CharacterClass.MELEE)
        self.api.action_wander(self.api.get_owned_characters())
        self.api.send_chat(random.choice(chat_list))

achi = Achi()

def every_tick(interface: API):
    achi.run(api=interface)