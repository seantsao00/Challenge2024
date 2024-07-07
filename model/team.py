from __future__ import annotations

from copy import deepcopy
from itertools import chain
from typing import TYPE_CHECKING

import const
import const.character
import const.team
from event_manager import (EventAttack, EventBulletCreate, EventBulletDisappear,
                           EventCharacterDied, EventCreateTower, EventEveryTick, EventHumanInput,
                           EventRangerBulletDamage, EventSelectCharacter, EventSniperBulletDamage,
                           EventSpawnCharacter, EventTeamGainTower, EventTeamLoseTower,
                           EventBulletCreate, EventBulletDisappear, EventRangerBulletDamage, EventSniperBulletDamage)
from instances_manager import get_event_manager, get_model
from model.character import Character, Melee, Character, Ranger, Sniper
from model.timer import Timer
from model.building import Tower

if TYPE_CHECKING:
    from model.building import Tower
    from model.bullet import Bullet
    from model.entity import Entity, LivingEntity


class NeutralTeam:

    """
    super class of class Team.
    """

    _total: int = 0

    def __init__(self, party: const.PartyType):
        self.__team_id = NeutralTeam._total
        self.__party = party
        NeutralTeam._total += 1

    @property
    def team_id(self) -> int:
        return self.__team_id

    @property
    def party(self) -> const.PartyType:
        return self.__party


class Team(NeutralTeam):

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

    def __init__(self, manual_control: bool, party: const.PartyType, team_name: str | None = None):
        super().__init__(party)

        self.__manual_control: bool = manual_control
        if team_name:
            self.__team_name = team_name
        else:
            self.__team_name = 'team' + str(self.__team_id)
        self.__points: int = 0
        self.__towers: set[Tower] = set()
        self.character_list: list[Character] = []
        self.__visible_entities_list: set[Entity] = set()
        self.__choosing_position: bool = False
        """For abilities that have to click mouse to cast."""
        self.__controlling: Entity | None = None
        self.register_listeners()

    def handle_input(self, event: EventHumanInput):
        """
        Handles input by human. This method is only used by human controlled teams.
        """
        def check_movable(entity: Entity, my_team: Team) -> bool:
            """
            This function checks if the clicked entity is actually movable by the human controlled team.
            """
            if entity is None:
                return False
            if isinstance(entity, Character) and entity.team is my_team and hasattr(entity, 'move'):
                return True
            return False

        def check_attackable(attacker: Entity, victim: Entity) -> bool:
            """
            This function checks if the clicked entity is able to be attacked and if the attacker is able to attack.
            """
            if attacker is None or not hasattr(attacker, 'attack') or not isinstance(attacker, Character):
                return False
            if victim is None or isinstance(attacker, Tower) and victim.is_fountain:
                return False
            return True

        clicked_entity = event.clicked_entity

        if event.input_type == const.InputTypes.PICK:
            if clicked_entity and clicked_entity.team is self:
                if self.__controlling is not None and isinstance(self.__controlling, Character):
                    self.__controlling.set_move_stop()
                self.__controlling = clicked_entity
            elif clicked_entity is not None:
                print('picked a non interactable entity')

        if self.__controlling is None:
            return

        if event.input_type == const.InputTypes.MOVE and check_movable(self.__controlling, self):
            self.__controlling.move(event.displacement)
        elif event.input_type == const.InputTypes.ATTACK:
            if isinstance(self.__controlling, Character):
                if self.__choosing_position is True:
                    self.__controlling.cast_ability(event.displacement)
                    self.__choosing_position = False
                elif check_attackable(victim=clicked_entity, attacker=self.__controlling):
                    self.__controlling.attack(clicked_entity)
        elif event.input_type is const.InputTypes.ABILITY:
            if isinstance(self.__controlling, Character):
                if isinstance(self.__controlling, Ranger):
                    self.__choosing_position = True
                else:
                    self.__controlling.cast_ability()

    def gain_character(self, event: EventSpawnCharacter):
        self.character_list.append(event.character)

    def gain_tower(self, event: EventTeamGainTower):
        if event.tower not in self.__towers:
            self.__towers.add(event.tower)
        print(f'{self.__team_name} gained a tower with id {event.tower.id} at {event.tower.position}')

    def lose_tower(self, event: EventTeamLoseTower):
        print(f'{self.__team_name} lost a tower with id {event.tower.id} at {event.tower.position}')
        if event.tower in self.__towers:
            self.__towers.remove(event.tower)

    def gain_point_kill(self):
        self.__points += const.SCORE_KILL

    def gain_point_tower(self, _: EventEveryTick):
        self.__points += const.SCORE_OWN_TOWER * len(self.__towers)

    def handle_character_died(self, event: EventCharacterDied):
        if self.__controlling is event.character:
            self.__controlling = None
        if event.character in self.character_list:
            self.character_list.remove(event.character)
        if event.character in self.visible_entities_list:
            self.visible_entities_list.remove(event.character)

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
                if (other_entity.team is not self
                        and other_entity.position.distance_to(entity.position) <= entity.attribute.vision):
                    self.visible_entities_list.add(other_entity)
        else:
            for my_entity in chain(self.__towers, self.character_list):
                if (my_entity.alive
                        and entity.position.distance_to(my_entity.position) <= my_entity.attribute.vision):
                    self.visible_entities_list.add(entity)
                    break

    def select_character(self, event: EventSelectCharacter):
        if isinstance(self.__controlling, Tower) and self.__controlling.team == self:
            print(f'Character type of Team {self.team_id} is modified to {event.character_type}')
            self.__controlling.update_character_type(event.character_type)

    def create_bullet(self, event: EventBulletCreate):
        if event.bullet.team == self:
            event.bullet.timer = Timer(interval=const.BULLET_INTERVAL,
                                       function=event.bullet.judge, once=False)

    def ranger_damage(self, event: EventRangerBulletDamage):
        if event.bullet.team == self:
            event.bullet.timer.__stop()
            model = get_model()
            for entity in model.entities:
                if (entity.position-event.bullet.target.position).length() < event.bullet.range and entity.team is not self:
                    get_event_manager().post(EventAttack(victim=entity, attacker=event.bullet.attacker), channel_id=entity.id)
            get_event_manager().post(EventBulletDisappear(bullet=event.bullet))

    def sniper_damage(self, event: EventSniperBulletDamage):
        if event.bullet.team == self:
            event.bullet.timer.__stop()
            get_event_manager().post(EventAttack(victim=event.bullet.victim,
                                                 attacker=event.bullet.attacker), channel_id=event.bullet.victim.id)
            get_event_manager().post(EventBulletDisappear(bullet=event.bullet))

    def bullet_disappear(self, event: EventBulletDisappear):
        if event.bullet.team == self:
            event.bullet.timer.__stop()
            event.bullet.hidden = True

    def register_listeners(self):
        """Register all listeners of this object with the event manager."""
        ev_manager = get_event_manager()
        if self.__manual_control:
            ev_manager.register_listener(EventHumanInput, self.handle_input)
        ev_manager.register_listener(EventCreateTower, self.handle_create_tower)
        ev_manager.register_listener(EventTeamGainTower, self.gain_tower, self.team_id)
        ev_manager.register_listener(EventTeamLoseTower, self.lose_tower, self.team_id)
        ev_manager.register_listener(EventSpawnCharacter, self.gain_character, self.team_id)
        ev_manager.register_listener(EventSelectCharacter, self.select_character)
        ev_manager.register_listener(EventCharacterDied, self.handle_character_died)
        ev_manager.register_listener(EventBulletCreate, self.create_bullet)
        ev_manager.register_listener(EventRangerBulletDamage, self.ranger_damage)
        ev_manager.register_listener(EventSniperBulletDamage, self.sniper_damage)
        ev_manager.register_listener(EventBulletDisappear, self.bullet_disappear)

    @property
    def team_name(self) -> str:
        return self.__team_name

    @property
    def points(self) -> int:
        return self.__points

    @property
    def towers(self) -> const.PartyType:
        return self.__towers

    @property
    def visible_entities_list(self):
        return self.__visible_entities_list
        if self.controlling is not None and hasattr(self.controlling, 'update_character_type'):
            if self.controlling.character_type != event.character:
                print(f'The character produced by team{self.id} is modified to {event.character}')
            self.controlling.update_character_type(event.character)
