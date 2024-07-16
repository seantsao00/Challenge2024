# import math
import random
import pygame as pg

from api.prototype import *

class StageClass(IntEnum):
    START = auto()
    EXPLOR = auto()
    ATTACK_TOWER = auto()
    DEFEN_TOWER = auto()
    ATTACK_ENEMY = auto()

class JerryAI:

    GRID_NUM: int = 20
    MAP_SIZE: int = 250
    PER_GRID: float =  MAP_SIZE / GRID_NUM

    EXPLORER_NUM: int = 20
    EXPLOR_WAITING_POINT: tuple[float, float] = (30, 30)
    EXPLORER_BOUND: float = GRID_NUM * GRID_NUM * 0.2

    def __init__(self):
        self.stage: StageClass = StageClass.START
        self.team_id: int = 0

        self.explor_map: set[tuple[int, int]] = set((i, j) for j in range(self.GRID_NUM) for i in range(self.GRID_NUM))
        self.exploring_grids: set[tuple[int, int]] = set()
        self.explored_grids: set[tuple[int, int]] = set()
        self.explorers: set[int] = set()

        self.my_chid_to_ch: dict[int: Character] = {}
        self.my_chs: set[int] = set()

        self.target_towerid: int = -1
        self.towerid_to_tower: dict[int, Tower] = {}

    def grid_to_coordiante(self, grid: tuple[int, int]) -> pg.Vector2:
        return pg.Vector2(JerryAI.PER_GRID * grid[0], JerryAI.PER_GRID * grid[1])

    def find_enemy_neutral_tower(self, api: API) -> bool:
        for tower in api.get_visible_towers():
            if not tower.is_fountain and tower.team_id != self.team_id:
                return True

    def explor(self, api:API, chids: set[int]):
        # explorer the map
        for chid in chids:
            des: tuple[int, int]
            if len(self.explor_map) == len(self.exploring_grids):
                des = random.sample(list(self.explor_map), 1)
            else:
                des = random.sample(list(self.explor_map - self.exploring_grids), 1)
                self.exploring_grids.add(des[0])
            api.action_move_to([self.my_chid_to_ch[chid]], self.grid_to_coordiante(des[0]))

    def attack_tower(self, api: API, tower: Tower):
        # attack the target tower
        api.action_move_to(api.get_owned_characters(), tower.position)
        for ch in api.get_owned_characters():
            if (tower.position - ch.position).length() <= ch.attack_range:
                print(tower.position)
                api.action_attack(api.get_owned_characters(), tower)
            else:
                enemies = api.within_attacking_range(ch, None)
                if  enemies is not None and len(enemies) != 0:
                    api.action_attack([ch], enemies[0])
                    
    def defen_tower(self, api: API, tower: Tower):
        for ch in api.get_owned_characters():
            api.action_move_to([ch], tower.position)
            enemies = api.within_attacking_range(ch, None)
            if enemies is not None and len(enemies) != 0:
                api.action_attack([ch], enemies[0])
            if self.find_enemy_neutral_tower(api):
                self.stage = StageClass.ATTACK_TOWER

    def stage_explor(self, api: API):
        self.explorers = self.my_chs & self.explorers
        unused: set[int] = self.my_chs - self.explorers
        # update exploers and unused character
        for chid in set(self.explorers):
            if api.get_movement(self.my_chid_to_ch[chid]).vector is None:
                self.explorers.remove(chid)
                unused.add(chid)
            

        # if the number of explorers is enough
        if self.EXPLORER_NUM > len(self.explorers):
            tmp = set(list(unused)[:self.EXPLORER_NUM - len(self.explorers)])
            self.explor(api, tmp)
            self.explorers |= tmp
        elif len(unused) > 0:
            tmp = [self.my_chid_to_ch[chid] for chid in unused]
            api.action_move_to(tmp, pg.Vector2(self.EXPLOR_WAITING_POINT[0], self.EXPLOR_WAITING_POINT[1]))
            api.change_spawn_type(api.get_owned_towers()[0], CharacterClass.MELEE)

    def stage_attack_tower(self, api: API):
        if self.target_towerid == -1 or self.towerid_to_tower[self.target_towerid].team_id == self.team_id:
            for t in api.get_visible_towers():
                if t.is_fountain or t.team_id == self.team_id:
                    continue
                self.target_towerid = t.id
                break

        self.attack_tower(api, self.towerid_to_tower[self.target_towerid])

    def stage_defence_tower(self, api: API):
        target_tower = None
        for t in api.get_owned_towers():
            if t.id == self.target_towerid:
                target_tower = self.towerid_to_tower[self.target_towerid]
                api.change_spawn_type(target_tower, CharacterClass.SNIPER)
                print(f"change tower {target_tower} to sniper")
                break

        if target_tower is None:
            self.stage = StageClass.ATTACK_ENEMY
        else:
            self.defen_tower(api, target_tower)
            


    def chat(self, api: API):
        # chs = api.get_owned_characters()
        emoji_list = [
            "(＾▽＾)", "(￣▽￣)", "(＾_＾)", "(￣ω￣)", "(￣︿￣)",
            "(Ｔ▽Ｔ)", "(≧ω≦)", "(￣へ￣)", "(＾◇＾)", "(＾ω＾)",
            "(⊙_⊙)", "(╥_╥)", "(ノಠ益ಠ)ノ", "(￣ー￣)", "(￣∇￣)",
            "(≧д≦)", "(＾Д＾)", "(￣□￣)", "(＾o＾)", "(￣︶￣)",
            "(￣ｰ￣)", "(＾▽＾*)", "(￣▽￣*)", "(＾◇＾*)", "(￣∇￣*)",
            "(￣ー￣*)", "(＾_＾*)", "(＾ω＾*)", "(￣︿￣*)", "(Ｔ▽Ｔ*)",
            "(≧ω≦*)", "(￣へ￣*)", "(＾◇＾;)", "(￣◇￣;)", "(￣∇￣;)",
            "(￣ー￣;)", "(＾ω＾;)", "(⊙_⊙;)", "(╥_╥;)", "(ノಠ益ಠ)ノ",
            "(￣ー￣)", "(￣︶￣)", "(Ｔ▽Ｔ)", "(≧д≦)", "(￣∇￣)",
            "(＾o＾)", "(＾◇＾)", "(＾_＾)", "(￣ω￣)", "(￣︿￣)", "(╯°□°）╯︵ ┻━┻"
        ]

        ch = random.choice(emoji_list)
        api.send_chat(ch)

    def run(self, api: API):
        self.my_chid_to_ch = {}
        self.my_chs = set()

        for character in api.get_owned_characters():
            self.my_chid_to_ch[character.id] = character
            self.my_chs.add(character.id)

        for tower in api.get_visible_towers():
            self.towerid_to_tower[tower.id] = tower

        if self.stage is StageClass.START:
            # Setting at the beginning
            api.change_spawn_type(api.get_owned_towers()[0], CharacterClass.MELEE)
            self.stage = StageClass.EXPLOR
            self.team_id = api.get_team_id()

        if self.stage is StageClass.EXPLOR:
            # Explore New Regions
            self.stage_explor(api)

            if self.find_enemy_neutral_tower(api):
                self.stage = StageClass.ATTACK_TOWER
            # elif api.get_current_time() > 30 or  len(explor_map) - len(explored_grids) <= 50:
            #     stage = StageClass.ATTACK_ENEMY
            self.chat(api)

        elif self.stage is StageClass.ATTACK_TOWER:
            # Attack towers
            print(f"Jerry's team {self.team_id} | Stage: ATTACK_TOWER")
            if not self.find_enemy_neutral_tower(api):
                api.send_chat("打下塔了哈哈。")
                self.stage = StageClass.DEFEN_TOWER

            self.stage_attack_tower(api)

        elif self.stage is StageClass.DEFEN_TOWER:
            print(f"Jerry's team {self.team_id} | Stage: DEFEN_TOWER")
            self.stage_defence_tower(api)
            if self.towerid_to_tower[self.team_id] not in api.get_owned_towers():
                self.stage = StageClass.ATTACK_TOWER

        elif self.stage == StageClass.ATTACK_ENEMY:
            print(f"Jerry's team {self.team_id} | Stage: ATTACK_ENEMY")
        else:
            print("missing stage")
            exit()

jerryai = JerryAI()

def every_tick(api: API):
    jerryai.run(api)
