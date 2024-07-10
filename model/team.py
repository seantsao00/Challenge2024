from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

import const
import const.team
from event_manager import (EventCharacterDied, EventCreateTower, EventEveryTick, EventHumanInput,
                           EventSelectCharacter, EventSpawnCharacter, EventTeamGainTower,
                           EventTeamLoseTower)
from instances_manager import get_event_manager
from model.building import Tower
from model.character import Character, Ranger
from util import log_info

if TYPE_CHECKING:
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


class Team_Vision:
    def __init__(self):
        self.N = int(const.ARENA_SIZE[0] / const.VISION_BLOCK_SIZE)
        self.M = int(const.ARENA_SIZE[1] / const.VISION_BLOCK_SIZE)
        self.mask: pg.Surface = pg.Surface((self.N, self.M), pg.SRCALPHA)
        self.mask.fill([0, 0, 0])
        self.mask.set_alpha(192)
        self.bool_mask: list[list[bool]] = [[False for _ in range(self.M)] for __ in range(self.N)]
        self.vision_not_open: list[list[int]] = [[0 for _ in range(int(self.M // const.TEAM_VISION_BLOCK) + 1)]
                                                 for __ in range(int(self.N // const.TEAM_VISION_BLOCK) + 1)]
        for x in range(self.N):
            for y in range(self.M):
                self.vision_not_open[x // const.TEAM_VISION_BLOCK][y //
                                                                   const.TEAM_VISION_BLOCK] += 1

    def transfer_to_pixel(self, position: pg.Vector2):
        return pg.Vector2(int(position.x / const.VISION_BLOCK_SIZE), int(position.y / const.VISION_BLOCK_SIZE))

    def transfer_to_heuristic(self, position: pg.Vector2):
        return pg.Vector2(int(position.x / const.VISION_BLOCK_SIZE / const.TEAM_VISION_BLOCK), int(position.y / const.VISION_BLOCK_SIZE / const.TEAM_VISION_BLOCK))

    def position_inside_vision(self, position: pg.Vector2) -> bool:
        pixel = self.transfer_to_pixel(position)
        if 0 <= pixel.x < self.N and 0 <= pixel.y < self.M:
            return self.bool_mask[int(pixel.x)][int(pixel.y)]
        return False

    def entity_inside_vision(self, entity: Entity):
        return self.position_inside_vision(entity.position)

    def get_mask(self):
        return self.mask

    def heuristic_test(self, position: pg.Vector2):
        bx, by = self.transfer_to_heuristic(position)
        bx, by = int(bx), int(by)
        for x in range(max(0, bx - 1), min(len(self.vision_not_open), bx + 2)):
            for y in range(max(0, by - 1), min(len(self.vision_not_open[0]), by + 2)):
                if self.vision_not_open[x][y] > 0:
                    return True
                if self.vision_not_open[x][y] < 0:
                    raise NotImplementedError
        return False

    def brute_modify(self, position: pg.Vector2, radius: float):
        real_position = self.transfer_to_pixel(position)
        real_radius = radius / const.VISION_BLOCK_SIZE
        for x in range(max(0, int(real_position.x - real_radius)),
                       min(self.N, int(position.x + real_radius + 1))):
            for y in range(max(0, int(real_position.y - real_radius)),
                           min(self.M, int(position.y + real_radius + 1))):
                if position.distance_to(pg.Vector2(const.VISION_BLOCK_SIZE * (x + 0.5), const.VISION_BLOCK_SIZE * (y + 0.5))) <= radius:
                    a = self.mask.get_at((x, y))
                    if a[3] != 0:
                        a[3] = 0
                        self.vision_not_open[x
                                             // const.TEAM_VISION_BLOCK][y // const.TEAM_VISION_BLOCK] -= 1
                        self.bool_mask[x][y] = True
                        self.mask.set_at((x, y), a)

    def update_vision(self, entity: LivingEntity):
        if entity.alive is False or self.heuristic_test(entity.position) is False:
            return
        self.brute_modify(entity.position, entity.attribute.vision)


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
        self.character_list: set[Character] = set()
        self.fountain: Tower = None
        self.__choosing_position: bool = False
        """For abilities that have to click mouse to cast."""
        self.__controlling: Entity | None = None
        self.vision = Team_Vision()
        self.register_listeners()

    def handle_input(self, event: EventHumanInput):
        """
        Handles input by human. This method is only used by human controlled teams.
        """
        clicked_entity = event.clicked_entity

        if event.input_type == const.InputTypes.PICK:
            if clicked_entity and clicked_entity.team is self:
                if self.__controlling is not None and isinstance(self.__controlling, Character):
                    self.__controlling.set_move_stop()
                self.__controlling = clicked_entity
            else:
                log_info('picked a non interactable entity')

        if self.__controlling is None:
            return

        if event.input_type == const.InputTypes.MOVE and isinstance(self.__controlling, Character):
            self.__controlling.set_move_direction(event.displacement)
        elif event.input_type == const.InputTypes.ATTACK:
            if isinstance(self.__controlling, Character):
                if self.__choosing_position is True:
                    self.__controlling.cast_ability(event.displacement)
                    self.__choosing_position = False
                elif isinstance(clicked_entity, (Tower, Character)):
                    self.__controlling.attack(clicked_entity)
        elif event.input_type is const.InputTypes.ABILITY:
            if isinstance(self.__controlling, Character):
                if isinstance(self.__controlling, Ranger):
                    self.__choosing_position = True
                else:
                    self.__controlling.cast_ability()

    def gain_character(self, event: EventSpawnCharacter):
        self.character_list.add(event.character)

    def gain_tower(self, event: EventTeamGainTower):
        if event.tower not in self.__towers:
            self.__towers.add(event.tower)
        if self.fountain == None:
            self.fountain = event.tower
        log_info(f'{self.__team_name} gained a tower '
                 f'with id {event.tower.id} at {event.tower.position}')

    def lose_tower(self, event: EventTeamLoseTower):
        log_info(f'{self.__team_name} lost a tower '
                 f'with id {event.tower.id} at {event.tower.position}')
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

    def handle_create_tower(self, event: EventCreateTower):
        if event.tower.team is self:
            self.update_vision(event.tower)

    def handle_others_character_spawn(self, event: EventSpawnCharacter):
        if event.character.team is self:
            self.update_vision(event.character)

    def update_vision(self, entity: LivingEntity):  # to do
        self.vision.update_vision(entity)

    def select_character(self, event: EventSelectCharacter):
        if isinstance(self.__controlling, Tower):
            self.__controlling.update_character_type(event.character_type)

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

    @property
    def team_name(self) -> str:
        return self.__team_name

    @property
    def points(self) -> int:
        return self.__points

    @property
    def towers(self) -> const.PartyType:
        return self.__towers

    # @property
    # def visible_entities_list(self):
    #     return self.__visible_entities_list
