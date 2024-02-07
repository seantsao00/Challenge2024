import pygame as pg

from event_manager.event_manager import BaseEvent


class EventInitialize(BaseEvent):
    name = "Initialize event"


class EventQuit(BaseEvent):
    name = "Quit event"


class EventPauseModel(BaseEvent):
    name = 'PauseModel event'


class EventContinueModel(BaseEvent):
    name = 'ContinueModel event'


class EventEveryTick(BaseEvent):
    name = "Tick event"


class EventPlayerMove(BaseEvent):
    name = "PlayerMove event"
