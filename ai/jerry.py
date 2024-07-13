import math
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

        self.own_character_dict: dict[int: Character] = dict()
        self.owned_characters: set[int] = set()

        self.target_tower_id: int = -1
        self.tower_id_to_entity: dict[int, Tower] = dict()

    def grid_to_coordiante(self, grid: tuple[int, int]) -> pg.Vector2:
        return pg.Vector2(JerryAI.PER_GRID * grid[0], JerryAI.PER_GRID * grid[1])

    def find_enemy_neutral_tower(self, api: API) -> bool:
        for tower in api.get_visible_towers():
            if not tower.is_fountain and tower.team_id != self.team_id:
                return True

    def explor(self, api:API, characters: set[int]):
        for _, chid in enumerate(characters):
            des: tuple[int, int]
            if len(self.explor_map) == len(self.exploring_grids):
                des = random.sample(list(self.explor_map), 1)
            else:
                des = random.sample(list(self.explor_map - self.exploring_grids), 1)
                self.exploring_grids.add(des[0])
            api.action_move_to([self.own_character_dict[chid]], self.grid_to_coordiante(des[0]))

    def attack_tower(self, api: API, tower: Tower):
        api.action_move_to(api.get_owned_characters(), tower.position)
        for ch in api.get_owned_characters():
            if (tower.position - ch.position).length() <= ch.attack_range:
                api.action_attack(api.get_owned_characters(), tower)
            else:
                enemies = api.within_attacking_range(ch, None)
                if  enemies is not None and len(enemies) != 0:
                    api.action_attack([ch], enemies[0])


    def stage_explor(self, api: API):
        self.explorers = self.owned_characters & self.explorers
        unused: set[int] = self.owned_characters - self.explorers
        # update exploers and unused character
        for chid in set(self.explorers):
            if api.get_movement(self.own_character_dict[chid]).vector is None:
                self.explorers.remove(chid)
                unused.add(chid)

        # if the number of explorers is enough
        if self.EXPLORER_NUM > len(self.explorers):
            tmp = set(list(unused)[:self.EXPLORER_NUM - len(self.explorers)])
            self.explor(api, tmp)
            self.explorers |= tmp
        elif len(unused) > 0:
            tmp = [self.own_character_dict[chid] for chid in unused]
            api.action_move_to(tmp, pg.Vector2(self.EXPLOR_WAITING_POINT[0], self.EXPLOR_WAITING_POINT[1]))
            api.change_spawn_type(api.get_owned_towers()[0], CharacterClass.RANGER)

    def stage_attack_tower(self, api: API):
        if self.target_tower_id == -1 or self.tower_id_to_entity[self.target_tower_id].team_id == self.team_id:
            for t in api.get_visible_towers():
                if t.is_fountain or t.team_id == self.team_id:
                    continue
                target_tower_id = t.id
                break
        self.attack_tower(api, self.tower_id_to_entity[target_tower_id])

    # def stage_defence(api: API):
    def chat(self, api: API):
        # chs = api.get_owned_characters()
        emoji_list = [
            "(｡♥‿♥｡)", "(≧◡≦)", "(≧ω≦)", "(◕‿◕✿)", "(づ｡◕‿‿◕｡)づ",
            "(ʘ‿ʘ)", "(｡◕‿◕｡)", "(♥ω♥*)", "(¬‿¬)", "(✿◠‿◠)",
            "(╯°□°）╯︵ ┻━┻", "(≧▽≦)", "( ͡° ͜ʖ ͡°)", "(✧ω✧)", "(ᵔᴥᵔ)",
            "(^_^)", "(ಠ_ಠ)", "(╯︵╰,)", "(T_T)", "(ಥ﹏ಥ)",
            "(｡•́︿•̀｡)", "(ʘ‿ʘ)", "(•̀ᴗ•́)و ̑̑", "(￣ω￣)", "(￣3￣)",
            "( ͡ᵔ ͜ʖ ͡ᵔ )", "(◕‿◕✿)", "( ͡° ͜ʖ ͡°)", "(ღ˘⌣˘ღ)", "(✪ω✪)",
            "(◕‿◕)", "(•ω•)", "(●‿●)", "(≧◡≦)", "(≧ω≦)",
            "(✧ω✧)", "(✿◠‿◠)", "(╯°□°）╯︵ ┻━┻", "(≧▽≦)", "( ͡° ͜ʖ ͡°)",
            "(｡♥‿♥｡)", "(≧◡≦)", "(≧ω≦)", "(◕‿◕✿)", "(づ｡◕‿‿◕｡)づ",
            "(ʘ‿ʘ)", "(｡◕‿◕｡)", "(♥ω♥*)", "(¬‿¬)", "(✿◠‿◠)"
        ]

        ch = random.choice(emoji_list)
        api.send_chat(ch)

    def run(self, api: API):
        self.own_character_dict = dict()
        self.owned_characters = set()

        for character in api.get_owned_characters():
            self.own_character_dict[character.id] = character
            self.owned_characters.add(character.id)

        for tower in api.get_visible_towers():
            self.tower_id_to_entity[tower.id] = tower

        if self.stage is StageClass.START:
            # Setting at the beginning
            api.change_spawn_type(api.get_owned_towers()[0], CharacterClass.MELEE)
            self.stage = StageClass.EXPLOR
            team_id = api.get_team_id()

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
            print(f"Jerry's team {team_id} | Stage: ATTACK_TOWER")
            if not self.find_enemy_neutral_tower(api):
                api.send_chat("打下塔了哈哈。")
                self.stage = StageClass.DEFEN_TOWER
            self.stage_attack_tower(api)

        elif self.stage is StageClass.DEFEN_TOWER:
            print(f"Jerry's team {team_id} | Stage: DEFEN_TOWER")
            for ch in api.get_owned_characters():
                enemies = api.within_attacking_range(ch, None)
                if  enemies is not None and len(enemies) != 0:
                    api.action_attack([ch], enemies[0])
            if self.find_enemy_neutral_tower(api):
                self.stage = StageClass.ATTACK_TOWER

        elif self.stage == StageClass.ATTACK_ENEMY:
            print("error")
            exit()

        else:
            print("missing stage")
            exit()

jerryai = JerryAI()

def every_tick(api: API):
    jerryai.run(api)
