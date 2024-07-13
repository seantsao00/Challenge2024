import math
import random
import pygame as pg

from api.prototype import *

# constant
class StageClass(IntEnum):
    START = auto()
    EXPLOR = auto()
    ATTACK_TOWER = auto()
    DEFEN_TOWER = auto()
    ATTACK_ENEMY = auto()

GRID_NUM: int = 20
MAP_SIZE: int = 250
PER_GRID: float =  MAP_SIZE / GRID_NUM

EXPLORER_NUM: int = 20
EXPLOR_WAITING_POINT: tuple[float, float] = (30, 30)
EXPLORER_BOUND: float = GRID_NUM * GRID_NUM * 0.2


# variable
stage: StageClass = StageClass.START
team_id: int = 0

explor_map: set[tuple[int, int]] = set((i, j) for j in range(GRID_NUM) for i in range(GRID_NUM))
exploring_grids: set[tuple[int, int]] = set()
explored_grids: set[tuple[int, int]] = set()
explorers: set[int] = set()

own_character_dict: dict[int: Character] = dict()
owned_characters: set[int] = set()

target_tower_id: int = -1
tower_id_to_entity: dict[int, Tower] = dict()

def grid_to_coordiante(grid: tuple[int, int]) -> pg.Vector2:
    return pg.Vector2(PER_GRID * grid[0], PER_GRID * grid[1])

def find_enemy_neutral_tower(api: API) -> bool:
    global team_id
    for tower in api.get_visible_towers():
        if not tower.is_fountain and tower.team_id != team_id:
            return True

def explor(api:API, characters: set[int]):
    global own_character_dict
    for _, chid in enumerate(characters):
        des: tuple[int, int]
        if len(explor_map) == len(exploring_grids):
            des = random.sample(list(explor_map), 1)
        else:
            des = random.sample(list(explor_map - exploring_grids), 1)
            exploring_grids.add(des[0])
        api.action_move_to([own_character_dict[chid]], grid_to_coordiante(des[0]))
        # print(f"{chid}->{des[0]}|{grid_to_coordiante(des[0])}", end=" ")
    # print()

def attack_tower(api: API, tower: Tower):
    api.action_move_to(api.get_owned_characters(), tower.position)
    api.action_attack(api.get_owned_characters(), tower)

def stage_attack_tower(api: API):
    global team_id, target_tower_id, tower_id_to_entity
    if target_tower_id == -1 or tower_id_to_entity[target_tower_id].team_id == team_id:
        for t in api.get_visible_towers():
            if t.is_fountain or t.team_id == team_id:
                continue
            target_tower_id = t.id
            break
    attack_tower(api, tower_id_to_entity[target_tower_id])

def stage_explor(api: API):
    global explorers, owned_characters, own_character_dict

    # print(f"owned = {owned_characters}")
    explorers = owned_characters & explorers

    unused: set[int] = owned_characters - explorers

    # unused: set[int] = set()
    # print(f"unused = {unused}")
    # print(f"e = {explorers}")

    for chid in set(explorers):
        if api.get_movement(own_character_dict[chid]).vector is None:
            explorers.remove(chid)
            unused.add(chid)

    if EXPLORER_NUM > len(explorers):
        tmp = set(list(unused)[:EXPLORER_NUM - len(explorers)])
        explor(api, tmp)
        explorers |= tmp
    elif len(unused) > 0:
        tmp = [own_character_dict[chid] for chid in unused]
        api.action_move_to(tmp, pg.Vector2(EXPLOR_WAITING_POINT[0], EXPLOR_WAITING_POINT[1]))
        api.change_spawn_type(api.get_owned_towers()[0], CharacterClass.RANGER)


def every_tick(api: API):
    global own_character_dict, owned_characters, stage, team_id, tower_id_to_entity
    own_character_dict = dict()
    owned_characters = set()

    for character in api.get_owned_characters():
        own_character_dict[character.id] = character
        owned_characters.add(character.id)

    for tower in api.get_visible_towers():
        tower_id_to_entity[tower.id] = tower

    if stage is StageClass.START:
        # Setting at the beginning
        api.change_spawn_type(api.get_owned_towers()[0], CharacterClass.MELEE)
        stage = StageClass.EXPLOR
        team_id = api.get_team_id()
        
    if stage is StageClass.EXPLOR:
        # Explore New Regions
        stage_explor(api)
        
        if find_enemy_neutral_tower(api):
            stage = StageClass.ATTACK_TOWER
        # elif api.get_current_time() > 30 or  len(explor_map) - len(explored_grids) <= 50:
        #     stage = StageClass.ATTACK_ENEMY

    elif stage is StageClass.ATTACK_TOWER:
        # Attack towers
        print(f"Jerry's team {team_id} | Stage: ATTACK_TOWER")
        if not find_enemy_neutral_tower(api):
            stage = StageClass.DEFEN_TOWER
        stage_attack_tower(api)

    elif stage is StageClass.DEFEN_TOWER:
        print(f"Jerry's team {team_id} | Stage: DEFEN_TOWER")
        for ch in api.get_owned_characters():
            enemies = api.within_attacking_range(ch, None)
            if  enemies is not None and len(enemies) != 0:
                # print(enemies)
                api.action_attack([ch], enemies[0])
        if find_enemy_neutral_tower(api):
            stage = StageClass.ATTACK_TOWER


    elif stage == StageClass.ATTACK_ENEMY:
        print("error")
        exit()

    else:
        print("missing stage")
        exit()
        
    for ch in api.get_owned_characters():
        enemies = api.within_attacking_range(ch, None)
        if  enemies is not None and len(enemies) != 0:
            # print(enemies)
            api.action_attack([ch], enemies[0])
    # print([api.get_score_of_team(i) for i in range(0, 4)])
