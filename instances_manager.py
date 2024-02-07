"""
This manager manages global instances.
"""

__event_manager = None
__model = None


def register_event_manager(event_manager):
    global __event_manager
    __event_manager = event_manager


def get_event_manager():
    from event_manager.event_manager import EventManager
    event_manager: EventManager = __event_manager
    return event_manager


def register_model(model):
    global __model
    __model = model


def get_model():
    from model.model import Model
    model: Model = __model
    return model
