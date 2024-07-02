import os
import signal
import threading
import traceback

import pygame as pg

import api.api as api
import model
import model.character
from const import FPS, MAX_TEAMS
from instances_manager import get_model
import model.character.lookout
import model.character.melee
import model.character.ranged_fighter

__model = get_model()


class GameError(Exception):
    def __init__(self, message):            
        super().__init__("The game broke. This is not your fault. Please contact us so we can fix it." + message)

class Internal(api.API):
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.__character_map = {}
        self.__tower_map = {}
        self.__reverse_character_map = {}
        self.__reverse_tower_map = {}

    def clear_map(self):
        self.__character_map = {}
        self.__tower_map = {}
        self.__reverse_character_map = {}
        self.__reverse_tower_map = {}
    
    def __register_character(self, internal: model.Character) -> api.Character:
        """
        Register a `model.Character` to `api.Character`.
        Therefore, API can only manipulate a character using the given interface 
        while we still know the original `model.Character`.
        """

        if internal.id not in self.__character_map:
            character_class = api.CharacterClass.unknown
            if isinstance(internal, model.character.melee):
                character_class = api.CharacterClass.melee
            elif isinstance(internal, model.character.lookout):
                character_class = api.CharacterClass.lookout
            elif isinstance(internal, model.character.ranged_fighter):
                character_class = api.CharacterClass.ranged
            else:
                raise GameError("Unknown character type")
            extern = api.Character(
                _id = internal.id,
                _type = character_class,
                _position = internal.position,
                _speed = internal.speed,
                _attack_range = internal.attack_range,
                _damage = internal.damage,
                _vision = internal.vision,
                _health = internal.health,
                _max_health = internal.max_health,
                _team_id = internal.team.id
            )
            self.__character_map[internal.id] = extern
            self.__reverse_character_map[id(extern)] = internal
        return self.__character_map[internal.id]

    
    def __register_tower(self, internal: model.Tower) -> api.Tower:
        """
        Register a `model.Tower` to `api.Tower` like above.
        """
        if internal.id not in self.__tower_map:
            extern = api.Tower(
                _id = internal.id,
                _position = internal.position,
                _period = internal.period,
                _is_fountain = internal.is_fountain,
                _attack_range = internal.attack_range,
                _damage = internal.damage,
                _vision = internal.vision,
                _health = internal.health,
                _max_health = internal.max_health,
                _team_id = internal.team.id
            )
            self.__tower_map[internal.id] = extern
            self.__reverse_tower_map[id(extern)] = internal
        return self.__tower_map[internal.id]

    def __team(self):
        return __model.teams[self.player_id - 1]

    def get_time():
        return __model.clock.tick() * 1000

    def get_characters(self) -> list[api.Character]:
        return [self.__register_character(character) 
                for character in self.__team().character_list]

    def get_towers(self) -> list[api.Tower]:
        return [self.__register_tower(tower) 
                for tower in self.__team().building_list]

    def get_team_id(self) -> int:
        # Cast to prevent modification
        return self.__team().id

    def get_score(self, index=0) -> int:
        if not isinstance(index, int):
            raise TypeError("Team index must be type int.")
        if index == 0:
            index = self.player_id
        if index < 1 or MAX_TEAMS:
            raise IndexError
        team = __model.teams[index - 1]
        # Should be correct, if model implementation changes this should fail
        if not team.id == index:
            raise GameError("Team ID implement has changed.")
        return team.points


class Timer():
    def __init__(self):
        if os.name == 'nt':
            self.is_windows = True
        elif os.name == 'posix':
            self.is_windows = False
        else:  # os.name == 'java' or unknown
            raise OSError

        if not self.is_windows:
            def handler(sig, frame):
                raise TimeoutError()

            signal.signal(signal.SIGALRM, handler)
        self.timer = None
        self.for_player_id = None

    def set_timer(self, interval: float, player_id: int):
        if not self.is_windows:
            signal.setitimer(signal.ITIMER_REAL, interval)
        else:
            def timeout_alarm(player_id: int):
                print(f"The AI of player {player_id} time out!")

            self.timer = threading.Timer(interval=interval, function=timeout_alarm,
                                         args=[player_id])
            self.timer.start()

    def cancel_timer(self):
        try:
            if not self.is_windows:
                signal.setitimer(signal.ITIMER_REAL, 0)
            else:
                self.timer.cancel()
        except:
            print("Perhaps some very slightly timeout.")


helpers = [Internal(i) for i in range(MAX_TEAMS)]
ai = [None] * len(helpers)
timer = Timer()


def init_ai(files):
    raise NotImplementedError


def call_ai(player_id):
    if ai[player_id] is None:
        return

    try:
        timer.set_timer(1 / (4 * FPS), player_id)
        ai[player_id].player_tick()
    except Exception as e:
        print(f"Caught exception in AI of {player_id}:")
        print(traceback.format_exc())
        return
    finally:
        timer.cancel_timer()
