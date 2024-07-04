from __future__ import annotations

from itertools import chain
from typing import TYPE_CHECKING

import pygame as pg

import const
import const.character
import const.team
from event_manager import (EventBulletCreate, EventBulletDisappear, EventCharacterDied,
                           EventCharacterMove, EventCreateTower, EventEveryTick, EventHumanInput,
                           EventRangerBulletDamage, EventSelectCharacter, EventSniperBulletDamage,
                           EventSpawnCharacter, EventTeamGainTower, EventTeamLoseTower)
from instances_manager import get_event_manager, get_model
from model.character import RangerFighter

if TYPE_CHECKING:
    from model.building import Tower
    from model.character import Character, Melee, RangerFighter, Sniper
    from model.entity import Entity, LivingEntity


class Team:

    """
    Class for Team in the game.
    Each Team has the following property:
     - name: The name of the team.
     - master: The controller of the team.
     - total_buildings: The total buildings that this team has.
     - points: The accumulated points of the team.
     - id: The id of the team.
     - building_list: list of the building of the team. The first one is the fountain.
     - character_list: list of the character of the team.
     - visible_entities_list: list of visible entities to the team. Note that entities owned by this team is not in this list.
    """

    total = 0

    def __init__(self, fountain_position: pg.Vector2, name: str, master: str):
        if Team.total == 4:
            raise Exception('Team size exceeds.')
        Team.total += 1
        self.id = Team.total
        self.name = name
        self.points = 0
        self.master = master
        self.building_list: list[Tower] = []
        self.character_list: list[Character] = []
        self.visible_entities_list: set[Entity] = set()
        self.choose_position = False
        self.controlling = None
        if master == 'human':
            get_event_manager().register_listener(EventHumanInput, self.handle_input)
        get_event_manager().register_listener(EventCreateTower, self.handle_create_tower)
        get_event_manager().register_listener(EventTeamGainTower, self.gain_tower, self.id)
        get_event_manager().register_listener(EventTeamLoseTower, self.lose_tower, self.id)
        get_event_manager().register_listener(EventSpawnCharacter, self.gain_character, self.id)
        get_event_manager().register_listener(EventSelectCharacter, self.select_character)
        get_event_manager().register_listener(EventBulletCreate, self.create_bullet)
        get_event_manager().register_listener(EventRangerBulletDamage, self.ranger_damage)
        get_event_manager().register_listener(EventSniperBulletDamage, self.sniper_damage)
        get_event_manager().register_listener(EventBulletDisappear, self.bullet_disappear)

    def handle_input(self, event: EventHumanInput):
        """
        Handles input by human. This method is only used by human controlled teams.
        """
        def check_movable(entity: Entity, my_team: Team):
            """
            This function checks if the clicked entity is actually movable by the human controlled team.
            """
            if entity is None:
                return False
            if hasattr(entity, 'team') and entity.team is my_team and hasattr(entity, 'move'):
                return True
            return False

        clicked = None
        clicked_type = const.CharTypes.NONE

        if event.clicked is not None and event.clicked.type == 'tower':
            clicked = event.clicked
            clicked_type = const.CharTypes.TOWER
        elif event.clicked is not None:
            clicked = event.clicked
            clicked_type = const.CharTypes.CHAR

        if event.input_type == const.InputTypes.PICK:
            if clicked_type == const.CharTypes.TOWER:
                if hasattr(clicked, 'update_character_type') and clicked.team is self:
                    self.controlling = clicked
                else:
                    print('clicked on non interactable tower')
            elif clicked_type == const.CharTypes.CHAR:
                if check_movable(clicked, self):
                    self.controlling = clicked
                else:
                    print('clicked on non interactable entity')

        if event.input_type == const.InputTypes.MOVE and check_movable(self.controlling, self):
            self.controlling.move(event.displacement)
        elif event.input_type == const.InputTypes.ATTACK and self.controlling is not None:
            if self.choose_position is True and hasattr(self.controlling, 'call_abilities'):
                self.controlling.call_abilities(event.displacement)
                self.choose_position = False
            elif clicked is not None and hasattr(self.controlling, 'attack'):
                self.controlling.attack(clicked)

        elif event.input_type == const.InputTypes.ABILITIES and self.controlling is not None:
            if isinstance(self.controlling, RangerFighter):
                self.choose_position = True
            elif hasattr(self.controlling, 'call_abilities'):
                self.controlling.call_abilities()

    def gain_character(self, event: EventSpawnCharacter):
        self.character_list.append(event.character)

    def gain_tower(self, event: EventTeamGainTower):
        if event.tower not in self.building_list:
            self.building_list.append(event.tower)
        print(self.id, " gained a tower with id",
              event.tower.id, " at", event.tower.position)

    def lose_tower(self, event: EventTeamLoseTower):
        print(self.id, " lost a tower with id", event.tower.id, " at", event.tower.position)
        if event.tower in self.building_list:
            self.building_list.remove(event.tower)

    def gain_point_kill(self):
        b = 1
        self.points += b
        print(self.id, " gain", b, "points.")

    def gain_point_tower(self, event: EventEveryTick):
        a = 1
        self.points += a * len(self.building_list)
        print(self.id, " gain", a * len(self.building_list), "points.")

    def handle_character_died(self, character: Character):
        if self.controlling is character:
            self.controlling = None
            self.character_list.remove(character)
            if character in self.visible_entities_list:
                self.visible_entities_list.remove(character)

    def handle_create_tower(self, event: EventCreateTower):
        self.update_visible_entities_list(event.tower)

    def handle_others_character_spawn(self, event: EventSpawnCharacter):
        self.update_visible_entities_list(event.character)

    def update_visible_entities_list(self, entity: LivingEntity):
        """
        This function updates the current entities visible to the instance of Team.
        """
        if not entity.alive:
            return

        model = get_model()

        if entity.team is self:
            for other_entity in model.entities:
                if (other_entity.team is not self and
                        other_entity.position.distance_to(entity.position) <= entity.vision):
                    self.visible_entities_list.add(other_entity)
        else:
            for my_entity in chain(self.building_list, self.character_list):
                if my_entity.alive and entity.position.distance_to(my_entity.position) <= my_entity.vision:
                    self.visible_entities_list.add(entity)
                    break

    def select_character(self, event: EventSelectCharacter):
        if self.controlling is not None and hasattr(self.controlling, 'update_character_type'):
            self.controlling.update_character_type(event.character)
            print(f'The character produced by team{self.id} is modified to {event.character}')

    def create_bullet(self, event: EventBulletCreate):
        event.bullet.judge()

    def ranger_damage(self, event: EventRangerBulletDamage):
        model = get_model()
        for entity in model.entities:
            if (entity.position-event.bullet.target.position).length() < event.bullet.range and entity.team is not self:
                entity.take_damage(event.bullet.damage)

    def sniper_damage(self, event: EventSniperBulletDamage):
        event.bullet.victim.take_damage(event.bullet.damage)

    def bullet_disappear(self, event: EventBulletDisappear):
        event.bullet.exist = False
