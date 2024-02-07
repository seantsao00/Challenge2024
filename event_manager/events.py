import pygame as pg

from event_manager.event_manager import BaseEvent


class EventInitialize(BaseEvent):
    pass


class EventQuit(BaseEvent):
    pass


class EventPauseModel(BaseEvent):
    pass


class EventContinueModel(BaseEvent):
    pass


class EventEveryTick(BaseEvent):
    pass


class EventPlayerMove(BaseEvent):
    pass
