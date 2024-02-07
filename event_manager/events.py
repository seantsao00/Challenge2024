"""
The module defines events would be used by EventManager.
"""

import pygame as pg


class BaseEvent:
    """
    The superclass of all events.
    """

    def __init__(self):
        pass


class EventInitialize(BaseEvent):
    """Event which will be posted when a new round of game starts."""
    pass


class EventQuit(BaseEvent):
    """Event which will be posted when a game round ends."""
    pass


class EventPauseModel(BaseEvent):
    """
    Event which will be posted when the game is pause.

    For example, a listener which forcibly pauses all characters can be registered with this event.
    """
    pass


class EventContinueModel(BaseEvent):
    """
    Event which will be posted when the game resumes.

    For example, a listener which resumes timer of the game can be registered with this event.
    """
    pass


class EventEveryTick(BaseEvent):
    """Event which will be posted every tick."""
    pass


class EventPlayerMove(BaseEvent):
    """
    Event which will be posted when a user input to move a character is detected.

    For example, a listener which actually changes position of characters can be registered with this event.
    """
    pass
