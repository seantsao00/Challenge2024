"""
The module defines events used by EventManager.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

import pygame as pg

import const

if TYPE_CHECKING:
    from model import Character, Entity, Tower


@dataclass(kw_only=True)
class BaseEvent:
    """The superclass of all events."""
    _permanent: ClassVar[bool] = False

    @classmethod
    def permanent(cls):
        return cls._permanent


@dataclass(kw_only=True)
class EventInitialize(BaseEvent):
    """Event posted upon a new round of game starts."""
    _permanent: ClassVar[bool] = True


@dataclass(kw_only=True)
class EventQuit(BaseEvent):
    """Event posted upon quitting the game (closing the program)."""
    _permanent: ClassVar[bool] = True


@dataclass(kw_only=True)
class EventStartGame(BaseEvent):
    """
    Event posted upon starting the game.

    For example, press space at cover scene would leave cover and start the game.
    """
    _permanent: ClassVar[bool] = True


@dataclass(kw_only=True)
class EventPauseModel(BaseEvent):
    """
    Event posted upon pausing the game.

    For example, a listener which forcibly pauses all characters can be registered with this event.
    """
    _permanent: ClassVar[bool] = True


@dataclass(kw_only=True)
class EventResumeModel(BaseEvent):
    """
    Event posted upon resuming the game.

    For example, a listener which resumes the timer of the game can be registered with this event.
    """
    _permanent: ClassVar[bool] = True


@dataclass(kw_only=True)
class EventEveryTick(BaseEvent):
    """Event posted every tick when the game is not in pause state"""


@dataclass(kw_only=True)
class EventUnconditionalTick(BaseEvent):
    """Event posted every tick, regardless of whether the game is in a paused state or not."""
    _permanent: ClassVar[bool] = True


@dataclass(kw_only=True)
class EventRestartGame(BaseEvent):
    """Post this event when the game needs to restart."""
    _permanent: ClassVar[bool] = True


@dataclass(kw_only=True)
class EventHumanInput(BaseEvent):
    """
    Event posted upon moving a human controlled team.

    For example, a listener which draws position of characters can be registered with this event.
    """
    input_type: const.InputTypes
    clicked: Entity | None = None
    displacement: pg.Vector2 | None = None
    """The displacement vector representing the movement."""

    def __str__(self):
        if self.input_type == const.InputTypes.PICK:
            return f"Clicked at {self.clicked.id}"
        return f"Move {self.displacement}"


@dataclass(kw_only=True)
class EventSelectCharacter(BaseEvent):
    """When picking a tower, we could select charcters"""
    character: Character | None = None


@dataclass(kw_only=True)
class EventCreateEntity(BaseEvent):
    """Event posted when an entity is created."""
    _permanent: ClassVar[bool] = True
    entity: Entity


@dataclass(kw_only=True)
class EventDiscardEntity(BaseEvent):
    """Event posted when an entity is discarded."""


@dataclass(kw_only=True)
class EventAttack(BaseEvent):
    attacker: Entity
    victim: Entity


@dataclass(kw_only=True)
class EventCreateTower(BaseEvent):
    _permanent: ClassVar[bool] = True
    tower: Tower


@dataclass(kw_only=True)
class EventTeamGainTower(BaseEvent):
    tower: Tower


@dataclass(kw_only=True)
class EventTeamLoseTower(BaseEvent):
    tower: Tower


@dataclass(kw_only=True)
class EventSpawnCharacter(BaseEvent):
    character: Character


@dataclass(kw_only=True)
class EventCharacterMove(BaseEvent):
    character: Character
    original_pos: pg.Vector2


@dataclass(kw_only=True)
class EventCharacterDied(BaseEvent):
    character: Character
