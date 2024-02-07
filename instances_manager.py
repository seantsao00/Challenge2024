"""
This manager manages global instances.
"""

__event_manager = None
__game_engine = None


def register_event_manager(event_manager):
    global __event_manager
    __event_manager = event_manager


def get_event_manager():
    from event_manager.event_manager import EventManager
    event_manager: EventManager = __event_manager
    return event_manager


def register_game_engine(game_engine):
    global __game_engine
    __game_engine = game_engine


def get_game_engine():
    from model.model import GameEngine
    game_engine: GameEngine = __game_engine
    return game_engine
