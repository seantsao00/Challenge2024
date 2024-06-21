import pygame

class TimerManager:
    _timers = {}

    @classmethod
    def register_timer(cls, timer):
        cls._timers[timer.event_type] = timer

    @classmethod
    def unregister_timer(cls, event_type):
        if event_type in cls._timers:
            del cls._timers[event_type]

    @classmethod
    def handle_event(cls, event) -> bool:
        """Handle events for all timers. Returns True if handled."""
        timer = cls._timers.get(event.type)
        if timer:
            timer._handle_event(event)
            return True
        return False

class Timer:
    _next_event_type = pygame.USEREVENT + 30

    def __init__(self, interval, function, once=False, *args, **kwargs):
        """
        Initialize a Timer object.

        Parameters:
            interval (int):        The interval(ms) at which the function should be called.
            function (callable):   The function to call at each interval.
            once (bool):           If True, the timer will execute only once and then stop.
            *args:                 Variable length argument list for the function.
            **kwargs:              Arbitrary keyword arguments for the function.
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
        if not self.running:
            pygame.time.set_timer(self.event_type, self.interval)
            self.running = True

    def stop(self):
        pygame.time.set_timer(self.event_type, 0)
        self.running = False

    def set_interval(self, interval):
        self.interval = interval
        if self.running:
            self.stop()
            self.start()
    
    def get_interval(self):
        return self.interval

    def get_count(self):
        return self.count

    def delete(self):
        self.stop()
        TimerManager.unregister_timer(self.event_type)

    def _handle_event(self, event):
        if event.type == self.event_type:
            self.count += 1
            self.function(*self.args, **self.kwargs)
            if self.once:
                self.delete()
