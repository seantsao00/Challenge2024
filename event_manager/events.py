"""
The module defines events used by EventManager.
"""

from dataclasses import dataclass

import pygame as pg

import const
# from model.entity import Entity


@dataclass(kw_only=True)
class BaseEvent:
    """The superclass of all events."""


@dataclass(kw_only=True)
class EventInitialize(BaseEvent):
    """Event posted upon a new round of game starts."""


@dataclass(kw_only=True)
class EventQuit(BaseEvent):
    """Event posted upon quitting the game (closing the program)."""


@dataclass(kw_only=True)
class EventPauseModel(BaseEvent):
    """
    Event posted upon pausing the game.

    For example, a listener which forcibly pauses all characters can be registered with this event.
    """


@dataclass(kw_only=True)
class EventContinueModel(BaseEvent):
    """
    Event posted upon resuming the game.

    For example, a listener which resumes the timer of the game can be registered with this event.
    """


@dataclass(kw_only=True)
class EventEveryTick(BaseEvent):
    """Event posted every tick."""


@dataclass(kw_only=True)
class EventPlayerMove(BaseEvent):
    """
    Event posted upon moving a player.

    For example, a listener which draws position of characters can be registered with this event.
    """
    displacement: pg.Vector2
    """
    The displacement vector representing the movement.
    """
    player_id: const.PlayerIds

    def __str__(self):
        return f"Player {self.player_id} move {self.displacement}"


@dataclass(kw_only=True)
class EventCreateEntity(BaseEvent):
    """Event posted when an entity is created."""

    def __init__(self, entity):
        self.entity = entity
