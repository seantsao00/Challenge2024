import pygame as pg

from api.prototype import *


def every_tick(api: API):
    # 創造空的列表(list)，儲存所有視野可及的敵方士兵
    visible = []
    for character in api.get_visible_characters():
        if character.team_id != api.get_team_id():
            visible.append(character)

    BATCH_SIZE = 8

    my_team_id = api.get_team_id()
    my_tower = api.get_owned_towers()
    api.change_spawn_type(my_tower[0], CharacterClass.MELEE)
    # api.change_spawn_type(my_tower[0], CharacterClass.RANGER)
    # api.change_spawn_type(my_tower[0], CharacterClass.SNIPER)

    my_characters = api.get_owned_characters()

    danger = [tower for tower in api.get_visible_towers() if tower.team_id != my_team_id]
    for tower in danger:
        to_tower = api.within_attacking_range(tower, my_characters)
        my_characters = list(filter(lambda x: x in to_tower, my_characters))
        api.action_move_to(to_tower, tower.position)

    for i in range(len(visible)):
        if (i + 1) * BATCH_SIZE > len(my_characters):
            break
        api.action_move_to(my_characters[i * BATCH_SIZE: (i + 1) * BATCH_SIZE], visible[i].position)
        api.action_attack(my_characters[i * BATCH_SIZE: (i + 1) * BATCH_SIZE], visible[i])

    if len(visible) * BATCH_SIZE < len(my_characters):
        api.action_move_along(
            my_characters[len(visible) * BATCH_SIZE: len(my_characters) // BATCH_SIZE * BATCH_SIZE], pg.Vector2(225, 225))
