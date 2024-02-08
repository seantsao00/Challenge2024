"""
The module defines events used by EventManager.
"""

import pygame as pg

import const.const as const


class BaseEvent:
    """The superclass of all events."""

    def __init__(self):
        pass


class EventInitialize(BaseEvent):
    """Event which will be posted when a new round of game starts."""


class EventQuit(BaseEvent):
    """Event which will be posted when a game round ends."""


class EventPauseModel(BaseEvent):
    """
    Event which will be posted when the game is pause.

    For example, a listener which forcibly pauses all characters can be registered with this event.
    """


class EventContinueModel(BaseEvent):
    """
    Event which will be posted when the game resumes.

    For example, a listener which resumes timer of the game can be registered with this event.
    """


class EventEveryTick(BaseEvent):
    """Event which will be posted every tick."""


class EventPlayerMove(BaseEvent):
    """
    Event which will be posted when a user input to move a character is detected.

    For example, a listener which draws position of characters can be registered with this event.

    EventPlayerMove.direction is the displacement vector of that movement.
    The length of this vector corresponds to the player's movement speed.
    """

    def __init__(self, direction: pg.Vector2):
        super().__init__()
        self.direction = direction.normalize() * const.PLAYER_SPEED

    def __str__(self):
        return f"Player move {self.direction}"
