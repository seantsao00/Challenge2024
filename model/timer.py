from __future__ import annotations

import time
from typing import Callable

import pygame as pg

from event_manager import EventGameOver, EventPauseModel, EventResumeModel


class TimerManager:
    __timers: dict[int, Timer] = {}

    @classmethod
    def register_timer(cls, timer: Timer):
        cls.__timers[timer.event_type] = timer

    @classmethod
    def unregister_timer(cls, event_type: int):
        if event_type in cls.__timers:
            del cls.__timers[event_type]

    @classmethod
    def handle_event(cls, event: pg.Event) -> bool:
        """Handle events for all timers. Returns True if handled."""
        timer = cls.__timers.get(event.type)
        if timer:
            # pylint: disable=protected-access
            timer.handle_event(event)
            return True
        return False

    @classmethod
    def pause_all_timer(cls, _: EventPauseModel):
        for timer in cls.__timers.values():
            timer.pause()

    @classmethod
    def resume_all_timer(cls, _: EventResumeModel):
        for timer in cls.__timers.values():
            timer.resume()

    @classmethod
    def handle_game_over(cls, _: EventGameOver):
        for timer in cls.__timers.values():
            timer.pause()


class Timer:
    __next_event_type = pg.USEREVENT + 30

    def __init__(self, interval: int, function: Callable, *args, once: bool = False, **kwargs):
        """
        Initialize a Timer object.

        Parameters:
        - `interval`: The interval(ms) at which the function should be called.
        - `function`: The function to call at each interval.
        - `once`: If True, the timer will execute only once and then stop.
        - `*args`: Variable length argument list for the function.
        - `**kwargs`: Arbitrary keyword arguments for the function.
        """
        self.interval: int = interval
        self.__function: Callable = function
        self.__args = args
        self.__kwargs = kwargs
        self.event_type = Timer.__next_event_type
        self.__count: int = 0
        self.__running: bool = False
        self.__once: bool = once
        self.remaining_time: int | None = None

        Timer.__next_event_type += 1

        TimerManager.register_timer(self)

        self.__start()

    def __start(self):
        """Restart the timer."""
        if not self.__running:
            pg.time.set_timer(self.event_type, self.interval)
            self.remaining_time = self.interval
            self.last_time = time.time()
            self.__running = True

    def __stop(self):
        """Stop the timer."""
        self.__running = False
        pg.time.set_timer(self.event_type, 0)

    def pause(self):
        """Pause the timer."""
        if self.__running:
            self.remaining_time = self.get_remaining_time()
            self.__running = False
            pg.time.set_timer(self.event_type, 0)

    def resume(self):
        """Resume the timer."""
        if not self.__running:
            pg.time.set_timer(self.event_type, self.remaining_time)
            self.remaining_time = None
            self.__running = True

    def set_interval(self, interval: int):
        """Set a new interval for the timer."""
        self.interval = interval
        if self.__running:
            self.__stop()
            self.__start()

    def get_remaining_time(self) -> int:
        if self.__running:
            return int(max(0, self.remaining_time - (time.time() - self.last_time) * 1000))
        return self.remaining_time

    def get_interval(self):
        """Get the current interval of the timer."""
        return self.interval

    def get_count(self):
        """Get the count of how many times the timer has triggered."""
        return self.__count

    def delete(self):
        """Delete the timer."""
        self.__stop()
        TimerManager.unregister_timer(self.event_type)

    def handle_event(self, event: pg.Event):
        if event.type == self.event_type:
            self.__count += 1
            self.__function(*self.__args, **self.__kwargs)

            if self.__once:
                self.delete()
            elif self.__running:
                self.__stop()
                self.__start()
