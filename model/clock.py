import time

from event_manager import EventPauseModel, EventResumeModel
from instances_manager import get_event_manager


class Clock:
    def __init__(self):
        self.__start_time: float = time.time()
        self.__pause_start_time: float | None = None
        self.__total_paused_time: float = 0.0

        self.__register_listeners()

    def __handle_pause(self, _: EventPauseModel):
        self.__pause_start_time = time.time()

    def __handle_resume(self, _: EventResumeModel):
        self.__total_paused_time += (time.time() - self.__pause_start_time)
        self.__pause_start_time = None

    def __register_listeners(self):
        ev_manager = get_event_manager()
        ev_manager.register_listener(EventPauseModel, self.__handle_pause)
        ev_manager.register_listener(EventResumeModel, self.__handle_resume)

    def get_time(self):
        return (time.time() if self.__pause_start_time is None else self.__pause_start_time) - self.__start_time - self.__total_paused_time
