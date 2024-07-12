import math, itertools
import random
from ordered_set import OrderedSet
import pygame as pg

from api.prototype import *

entity_type = ['melee']
map = set((x, y) for x in range(18) for y in range(18))
        
gathering_point = pg.Vector2(20, 20)
attacker_team: list[list[list[int], list[int], list[int], int]] = []
attacker_melee: list[list[int]] = []
attacker_ranger: list[list[int]] = []
destination: list[int] = []
sniper_under_tower: dict[int, int] = {}
my_team_id = 0
alive: dict[int, Character | Tower] = dict()
used = set()

def count_defence(total_health, damage):
    if total_health > damage / 2 * 3:
        return 3 + (total_health - damage / 2 * 3) / damage
    return total_health / (damage / 2)

def handle_attack(api: API):
    global gathering_point, my_team_id, attacker_team, alive
    need_delete = set()
    for i in range(len(attacker_team)):
        total_size = 0
        attribute: list[tuple[pg.Vector2, float]] = [(None, 0), (None, 0), (None, 0)]
        for j in range(3):
            attacker_team[i][j] = [character for character in attacker_team[i][j] if character in alive]
        for j in range(3):
            if len(attacker_team[i][j]) != 0:
                total_size += len(attacker_team[i][j])
                attribute[j] = (alive[attacker_team[i][j][0]].position, alive[attacker_team[i][j][0]].attack_range)

        if (total_size == 0 or attacker_team[i][3] not in alive or alive[attacker_team[i][3]].team_id == my_team_id):
            need_delete.add(i)
            for x in itertools.chain(attacker_team[i][0], attacker_team[i][1], attacker_team[i][2]):
                if x in used:
                    used.remove(x)
            continue
        
        for j in range(3):
            if attribute[j][0] is not None and attribute[j][0].distance_to(alive[attacker_team[i][3]].position) < attribute[j][1]:
                api.action_move_clear([alive[_] for _ in attacker_team[i][j]])
                api.action_attack([alive[_] for _ in attacker_team[i][j]], alive[attacker_team[i][3]])
                if j != 0:
                    api.action_cast_ability([alivmy_meleee[_] for _ in attacker_team[i][j]], alive[attacker_team[i][3]].position)
            else:
                api.action_move_to([alive[_] for _ in attacker_team[i][j]], alive[attacker_team[i][3]].position)

        for j in range(3):
            for k in range(j + 1, 3):
                if attribute[j][0] is not None and attribute[k][0] is not None:
                    if attribute[j][0].distance_to(attribute[k][0]) >  attribute[k][1] - attribute[j][1] + 3:
                        api.action_move_clear([alive[_] for _ in attacker_team[i][j]])
                        break


    attacker_team = [attacker_team[_] for _ in range(len(attacker_team)) if _ not in need_delete]

        

def every_tick(api: API):
    global my_team_id, map, alive, gathering_point, attacker_melee, attacker_ranger, destination, attacker_team
    my_team_id = api.get_team_id()
    visible = api.get_visible_characters()
    my_character = api.get_owned_characters()
    my_melee = [melee for melee in my_character if melee.type == CharacterClass.MELEE and melee.id not in used]
    my_ranger = [ranger for ranger in my_character if ranger.type == CharacterClass.RANGER and ranger.id not in used]
    my_sniper = [sniper for sniper in my_character if sniper.type == CharacterClass.SNIPER and sniper.id not in used]
    visible_enemy= [character for character in visible if character.team_id != my_team_id]
    my_tower = api.get_owned_towers()
    visible_tower = [tower for tower in api.get_visible_towers() if tower.team_id != my_team_id and tower.is_fountain is False]
    
    alive.clear()
    for character in itertools.chain(visible, my_character, my_tower, visible_tower):
        alive[character.id] = character

    handle_attack(api)

    api.action_move_to(my_ranger, gathering_point)
    api.action_cast_ability(my_melee)

    if len(my_melee) < 3:
        for tower in my_tower:
            api.change_spawn_type(tower, CharacterClass.MELEE)

    if len(visible_tower) > 0:
        api.action_move_to(my_melee, gathering_point)
        best_choose = (1e9, None)
        for tower in visible_tower:
            total = 150
            for character in visible_enemy:
                if character.type is CharacterClass.MELEE:
                    total += 36
                elif character.type is CharacterClass.RANGER:
                    total += 72
                elif character.type is CharacterClass.SNIPER:
                    total += 150
            best_choose = min(best_choose, (total, tower))

        group_melee = [_.id for _ in my_melee if _.position.distance_to(gathering_point) < 1]
        group_ranger = [_.id for _ in my_ranger if _.position.distance_to(gathering_point) < 1]

        if len(group_ranger) < len(group_melee) and len(group_ranger) < 7:
            for tower in my_tower:
                api.change_spawn_type(tower, CharacterClass.RANGER)
        else:
            for tower in my_tower:
                api.change_spawn_type(tower, CharacterClass.MELEE)
        my_total_health = 0
        for melee in my_melee:
            print(melee.position, melee.position.distance_to(gathering_point))
            if melee.position.distance_to(gathering_point) < 1:
                my_total_health += melee.health
        if len(group_ranger) >= 3 and count_defence(my_total_health, best_choose[0]) >= 5:
            attacker_team.append([group_melee, group_ranger, [], best_choose[1].id])
            for character in itertools.chain(group_melee, group_ranger):
                used.add(character)
    else:
        mx = 0
        if len(map) > 0:
            for melee in my_melee:
                if (melee.position[0] // 14, melee.position[1] // 14) in map:
                    map.remove((melee.position[0] // 14, melee.position[1] // 14))
            mx = len(my_melee)
            if len(visible_enemy) > 0:
                mx = min(5, mx)
            for i in range(mx):
                w = my_melee[i]
                if api.get_movement(w).status is MovementStatusClass.STOPPED:
                    choose = random.choice(list(map))
                    for _ in range(25):
                        x, y = min((random.random() + choose[0]) * 14, 245), min((random.random() + choose[1]) * 14, 245)
                        if (api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OBSTACLE
                            and api.get_terrain(pg.Vector2(x, y)) is not MapTerrain.OUT_OF_BOUNDS):
                            api.action_move_to([w], pg.Vector2(x, y))
                            break
            api.action_move_to(my_melee[mx:], gathering_point)
            
        if len(visible_enemy) > 0:
            enemys: list[Character] = api.sort_by_distance(visible_enemy, gathering_point)
            enemys_melee = [x for x in enemys if x.type is CharacterClass.MELEE]
            enemys_ranger = [x for x in enemys if x.type is CharacterClass.RANGER]
            enemys_sniper = [x for x in enemys if x.type is CharacterClass.SNIPER]
            sm = enemys_sniper + enemys_melee
            mr = enemys_melee + enemys_ranger
            rsm = enemys_ranger + enemys_sniper + enemys_melee
            if len(sm) > 0:
                for i in range(mx, len(my_melee)):
                    if my_melee[i].id not in used:
                        attacker_team.append([[my_melee[i].id], [], [], sm[i % len(sm)].id])
            else:
                api.action_move_to([x for x in my_melee if x.id not in used], gathering_point)

            if len(mr) > 0:
                for i in range(len(my_ranger)):
                    if my_ranger[i].id not in used:
                        attacker_team.append([[my_ranger[i].id], [], [], mr[i % len(mr)].id])
            else:
                api.action_move_to([x for x in my_melee if x.id not in used], gathering_point)

            sniper_attack = set()
            for i in range(len(my_sniper)):
                if my_sniper[i].id not in used:
                    can_attack = [enemy for enemy in rsm if enemy.position.distance_to(my_sniper[i].position) <= my_sniper[i].attack_range]
                    if len(can_attack) == 0:
                        continue
                    have_victim = 0
                    for enemy in can_attack:
                        if enemy.id in sniper_attack:
                            continue
                        attacker_team.append([[my_sniper[i].id], [], [], enemy.id])
                        sniper_attack.add(enemy.id)
                        have_victim = 1
                        break
                    if have_victim == 0:
                        attacker_team.append([[my_sniper[i].id], [], [], can_attack[random().randint(0, len(can_attack) - 1)]])


                
            
