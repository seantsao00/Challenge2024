"""
The module defines events used by EventManager.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame as pg

import const

if TYPE_CHECKING:
    from model import (Bullet, BulletCommon, BulletRanger, Character, Entity, LivingEntity, Team,
                       Tower)


@dataclass(kw_only=True)
class BaseEvent:
    """The superclass of all events."""


@dataclass(kw_only=True)
class EventInitialize(BaseEvent):
    """Event posted upon a new round of game starts."""


@dataclass(kw_only=True)
class EventPostInitialize(BaseEvent):
    """
    Event posted after a new round of game starts.
    This event is a workaround of AI, because everything should be started before AI.
    """


@dataclass(kw_only=True)
class EventQuit(BaseEvent):
    """Event posted upon quitting the game (closing the program)."""


@dataclass(kw_only=True)
class EventSelectParty(BaseEvent):
    """
    Event posted upon starting selecting party.
    """


@dataclass(kw_only=True)
class EventChangeParty(BaseEvent):
    """Event posted when player is selecting parties"""
    select_input: tuple[const.PartySelectorInputType, tuple[int, int] | None]


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
class EventGameOver(BaseEvent):
    """
    Event posted upon game over.

    It happens when either one of the team wins, or the game reaches total game time).
    """


@dataclass(kw_only=True)
class EventEveryTick(BaseEvent):
    """Event posted every tick when the game is not in pause state"""


@dataclass(kw_only=True)
class EventUnconditionalTick(BaseEvent):
    """Event posted every tick, regardless of whether the game is in a paused state or not."""


@dataclass(kw_only=True)
class EventHumanInput(BaseEvent):
    """
    Event posted upon moving a human controlled team.

    For example, a listener which draws position of characters can be registered with this event.
    """
    input_type: const.InputTypes
    clicked_entity: Entity | None = None
    displacement: pg.Vector2 | None = None
    """The displacement vector representing the movement."""

    def __str__(self):
        if self.input_type is const.InputTypes.PICK:
            return f"Clicked at {self.clicked_entity.id}"
        return f"Move {self.displacement}"


@dataclass(kw_only=True)
class EventSelectCharacter(BaseEvent):
    """When picking a tower, we could select generated character type"""
    character_type: const.CharacterType | None = None


@dataclass(kw_only=True)
class EventCreateEntity(BaseEvent):
    """Event posted when an entity is created."""
    entity: Entity


@dataclass(kw_only=True)
class EventDiscardEntity(BaseEvent):
    """Event posted when an entity is discarded."""


@dataclass(kw_only=True)
class EventAttack(BaseEvent):
    attacker: LivingEntity
    victim: LivingEntity
    damage: float


@dataclass(kw_only=True)
class EventCreateTower(BaseEvent):
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


@dataclass(kw_only=True)
class EventBulletCreate(BaseEvent):
    bullet: Bullet


@dataclass(kw_only=True)
class EventBulletDamage(BaseEvent):
    bullet: BulletCommon


@dataclass(kw_only=True)
class EventRangedBulletDamage(BaseEvent):
    bullet: BulletRanger


@dataclass(kw_only=True)
class EventSniperBulletParticle(BaseEvent):
    bullet: BulletCommon


@dataclass(kw_only=True)
class EventBulletDisappear(BaseEvent):
    bullet: Bullet


@dataclass(kw_only=True)
class EventViewChangeTeam(BaseEvent):
    """Event to change view team"""


@dataclass(kw_only=True)
class EventViewPathSwitch(BaseEvent):
    """Event to turn on and off path"""


@dataclass(kw_only=True)
class EventViewShowRangeSwitch(BaseEvent):
    """Event to turn on and off show range"""


@dataclass(kw_only=True)
class EventUseRangerAbility(BaseEvent):
    position: pg.Vector2 | tuple[float, float]


@dataclass(kw_only=True)
class EventBulletExplode(BaseEvent):
    bullet: Bullet


@dataclass(kw_only=True)
class EventSendChat(BaseEvent):
    type: const.ChatMessageType
    team: Team
    text: str


@dataclass(kw_only=True)
class EventLoadUpdate(BaseEvent):
    msg: str


@dataclass(kw_only=True)
class EventResultChoseCharacter(BaseEvent):
    """ In result, second to fourth place are chosen."""


@dataclass(kw_only=True)
class EventResultWandering(BaseEvent):
    """ In result, scope left characters and start wandering."""


@dataclass(kw_only=True)
class EventResultChamp(BaseEvent):
    """ In result, the champion is announced."""


@dataclass(kw_only=True)
class EventNyanCat(BaseEvent):
    """What is this?"""
