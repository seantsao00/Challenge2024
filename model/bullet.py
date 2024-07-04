import pygame as pg
from model.entity import Entity

from typing import TYPE_CHECKING
from __future__ import annotations


if TYPE_CHECKING:
    from model.team import Team


class Bullet(Entity):
    def __init__(self, position: pg.Vector2 | tuple[float, float], direction: pg.Vector2 | tuple[float, float],
                 entity_type: str = 'bullet', team: Team = None, imgstate: str = 'default',
                 speed: float = 0.0) -> None:
        super().__init__(position, entity_type=entity_type, team=team, imgstate=imgstate)
        self.direction: pg.Vector2 | tuple[float, float] = direction
        self.speed: float = speed
        self.exist: bool = True
