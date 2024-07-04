"""
The module defines events used by EventManager.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame as pg

import const

if TYPE_CHECKING:
    from model.building import Tower
    from model.character import Character
    from model.entity import Entity


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
class EventStartGame(BaseEvent):
    """
    Event posted upon starting the game.

    For example, press space at cover scene would leave cover and start the game.
    """
    

@dataclass(kw_only=True)
class EventPauseModel(BaseEvent):
    """
    Event posted upon pausing the game.

    For example, a listener which forcibly pauses all characters can be registered with this event.
    """


@dataclass(kw_only=True)
class EventResumeModel(BaseEvent):
    """
    Event posted upon resuming the game.

    For example, a listener which resumes the timer of the game can be registered with this event.
    """


@dataclass(kw_only=True)
class EventEveryTick(BaseEvent):
    """Event posted every tick when the game is not in pause state"""


@dataclass(kw_only=True)
class EventUnconditionalTick(BaseEvent):
    """Event posted every tick, regardless of whether the game is in a paused state or not."""


class EventHumanInput(BaseEvent):
    """
    Event posted upon moving a human controlled team.

    For example, a listener which draws position of characters can be registered with this event.
    """

    def __init__(self, input_type: const.InputTypes, clicked: Character = None, displacement: pg.Vector2 = None):
        self.input_type: const.InputTypes = input_type
        self.clicked: Character = clicked  # When INPUT_TYPE is PICK or ATTACK
        self.displacement: pg.Vector2 = displacement  # When INPUT_TYPE is MOVE
        """
        The displacement vector representing the movement.
        """

    def __str__(self):
        if self.input_type == const.InputTypes.PICK:
            return f"Clicked at {self.clicked.id}"
        return f"Move {self.displacement}"
    

@dataclass(kw_only=True)
class EventPartySelection(BaseEvent):
    """Event posted when player is selecting parties"""


@dataclass(kw_only=True)
class EventCreateEntity(BaseEvent):
    """Event posted when an entity is created."""

    def __init__(self, entity: Entity):
        self.entity: Entity = entity


class EventAttack(BaseEvent):
    def __init__(self, attacker: Entity, victim: Entity):  # reference of two characters
        self.attacker: Entity = attacker
        self.victim: Entity = victim


class EventMultiAttack(BaseEvent):
    def __init__(self, attacker: Character, target: pg.Vector2, radius: float):
        self.attacker: Character = attacker
        self.target: pg.Vector2 = target
        self.radius: float = radius


class EventTeamGainTower(BaseEvent):
    def __init__(self, tower: Tower):
        self.tower: Tower = tower


class EventTeamLoseTower(BaseEvent):
    def __init__(self, tower: Tower):
        self.tower: Tower = tower


class EventSpawnCharacter(BaseEvent):
    def __init__(self, character: Character):
        self.character: Character = character


class EventCharacterMove(BaseEvent):
    def __init__(self, character: Character, original_pos: pg.Vector2):
        self.character: Character = character
        self.original_pos: pg.Vector2 = original_pos


class EventCharacterDied(BaseEvent):
    def __init__(self, character: Character):
        self.character: Character = character
