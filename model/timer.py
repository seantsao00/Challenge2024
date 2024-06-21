import pygame

class Timer:
    def __init__(self, interval: int, once: bool=False):
        self._interval = interval
        self._last_time = pygame.time.get_ticks()
        self._enabled = True
        self._once = once
        self._count = 0

    def check(self) -> bool:
        if not self._enabled:
            return False
        current_time = pygame.time.get_ticks()
        if current_time - self._last_time > self._interval:
            self._last_time = current_time
            if self._once:
                self._enabled = False
            self._count += 1
            return True
        return False
    
    def reset(self, interval=None) -> None:
        if interval:
            self._interval = interval
        self._last_time = pygame.time.get_ticks()
        self._enabled = True
        self._count = 0
    
    def set_interval(self, interval: int) -> None:
        self._interval = interval

    def stop(self) -> None:
        self._enabled = False

    def get_count(self) -> int:
        return self._count