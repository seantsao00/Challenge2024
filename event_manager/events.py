"""
The module defines events used by EventManager.
"""

import pygame as pg

import const


class BaseEvent:
    """The superclass of all events."""

    def __init__(self):
        pass


class EventInitialize(BaseEvent):
    """Event posted upon a new round of game starts."""


class EventQuit(BaseEvent):
    """Event posted upon quitting the game (closing the program)."""


class EventPauseModel(BaseEvent):
    """
    Event posted upon pausing the game.

    For example, a listener which forcibly pauses all characters can be registered with this event.
    """


class EventContinueModel(BaseEvent):
    """
    Event posted upon resuming the game.

    For example, a listener which resumes the timer of the game can be registered with this event.
    """


class EventEveryTick(BaseEvent):
    """Event posted every tick."""


class EventPlayerMove(BaseEvent):
    """
    Event posted upon moving a player.

    For example, a listener which draws position of characters can be registered with this event.
    """

    def __init__(self, direction: pg.Vector2):
        super().__init__()
        self.direction = direction.normalize() * const.PlayerSpeeds.WALK
        """
        The displacement vector representing the movement.
        The length of this vector corresponds to the player's movement speed.
        """

    def __str__(self):
        return f"Player move {self.direction}"
