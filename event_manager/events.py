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


class EventHumanInput(BaseEvent):
    """
    Event posted upon moving a human controlled team.

    For example, a listener which draws position of characters can be registered with this event.
    """

    def __init__(self, input_type: const.InputTypes, clicked: Character = None, displacement: pg.Vector2 = None):
        self.input_type = input_type
        self.clicked = clicked  # When INPUT_TYPE is PICK or ATTACK
        self.displacement = displacement  # When INPUT_TYPE is MOVE
        """
        The displacement vector representing the movement.
        """

    def __str__(self):
        if self.input_type == const.InputTypes.PICK:
            return f"Clicked at {self.clicked.id}"
        return f"Move {self.displacement}"


@dataclass(kw_only=True)
class EventCreateEntity(BaseEvent):
    """Event posted when an entity is created."""

    def __init__(self, entity: Entity):
        self.entity = entity


class EventAttack(BaseEvent):
    def __init__(self, attacker: Character, victim: Character):  # reference of two characters
        self.attacker = attacker
        self.victim = victim


class EventMultiAttack(BaseEvent):
    def __init__(self, attacker: Character, target: pg.Vector2, radius):
        self.attacker = attacker
        self.target = target
        self.raidus = radius


class EventTeamGainTower(BaseEvent):
    def __init__(self, tower: Tower):
        self.tower = tower


class EventTeamLoseTower(BaseEvent):
    def __init__(self, tower: Tower):
        self.tower = tower


class EventSpawnCharacter(BaseEvent):
    def __init__(self, character: Character):
        self.character = character
