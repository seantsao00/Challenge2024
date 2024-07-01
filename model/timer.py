from __future__ import annotations

import time
from typing import Callable

import pygame as pg

from event_manager import EventPauseModel, EventResumeModel


class TimerManager:
    _timers: dict[int, Timer] = {}

    @classmethod
    def register_timer(cls, timer: Timer):
        cls._timers[timer.event_type] = timer

    @classmethod
    def unregister_timer(cls, event_type: int):
        if event_type in cls._timers:
            del cls._timers[event_type]

    @classmethod
    def handle_event(cls, event: pg.Event) -> bool:
        """Handle events for all timers. Returns True if handled."""
        timer = cls._timers.get(event.type)
        if timer:
            # pylint: disable=protected-access
            timer._handle_event(event)
            return True
        return False

    @classmethod
    def pause_all_timer(cls, _: EventPauseModel):
        for timer in cls._timers.values():
            timer.pause()

    @classmethod
    def resume_all_timer(cls, _: EventResumeModel):
        for timer in cls._timers.values():
            timer.resume()


class Timer:
    _next_event_type = pg.USEREVENT + 30

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
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.event_type = Timer._next_event_type
        self.count = 0
        self.running = False
        self.once = once

        Timer._next_event_type += 1

        TimerManager.register_timer(self)

        self.start()

    def start(self):
        """Restart the timer."""
        if not self.running:
            pg.time.set_timer(self.event_type, self.interval)
            self.remaining_time = self.interval
            self.last_time = time.time()
            self.running = True

    def stop(self):
        """Stop the timer."""
        self.running = False
        pg.time.set_timer(self.event_type, 0)

    def pause(self):
        """Pause the timer."""
        if self.running:
            self.remaining_time = self.get_remaining_time()
            self.running = False
            pg.time.set_timer(self.event_type, 0)

    def resume(self):
        """Resume the timer."""
        if not self.running:
            pg.time.set_timer(self.event_type, self.remaining_time)
            self.last_time = time.time()
            self.running = True

    def set_interval(self, interval: int):
        """Set a new interval for the timer."""
        self.interval = interval
        if self.running:
            self.stop()
            self.start()

    def get_remaining_time(self):
        if self.running:
            return int(max(0, self.remaining_time - (time.time() - self.last_time) * 1000))
        else:
            return self.remaining_time

    def get_interval(self):
        """Get the current interval of the timer."""
        return self.interval

    def get_count(self):
        """Get the count of how many times the timer has triggered."""
        return self.count

    def delete(self):
        """Delete the timer."""
        self.stop()
        TimerManager.unregister_timer(self.event_type)

    def _handle_event(self, event: pg.Event):
        if event.type == self.event_type:
            self.count += 1
            self.function(*self.args, **self.kwargs)

            if self.once:
                self.delete()
            elif self.running:
                self.stop()
                self.start()
