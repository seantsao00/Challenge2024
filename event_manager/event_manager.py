"""
The module defines EventManager.
"""

from collections import defaultdict
from typing import Callable, TypeAlias

from event_manager.events import BaseEvent
from util import log_warning

ListenerCallback: TypeAlias = Callable[[BaseEvent], None]
"""
The type of callback function used by listeners.

It is a function accepts one "Class" parameter,
which is a subclass of BaseEvent, and returns None
"""
ChannelId: TypeAlias = int


class EventManager:
    """
    Manager overseeing all events and their associated callback functions.

    This object serves as the coordinator between the model, view, and controller.

    To be precise, a listener is registered by providing a specific event and a callback function.
    When the event is actually posted, all callback functions bound to that event will be executed.

    There may be several channels for the same event type. Events are posted within the channel and
    are not shared between different channels. It may be useful when we want some specific recipient
    to get notified, but there are many listeners for the same type of events.
    """

    def __init__(self):
        self.__listeners: defaultdict[tuple[type[BaseEvent], ChannelId | None],
                                      set[ListenerCallback]] = defaultdict(set)

        self.__wait_remove_listeners: list[tuple[tuple[type[BaseEvent], ChannelId | None],
                                                 ListenerCallback]] = []
        self.__read_lock: int = 0
        """The lock to ensure one can modify self.listeners only when no one is iterating it."""

    def register_listener(self, event_class: type[BaseEvent],
                          listener: ListenerCallback, channel_id: ChannelId | None = None):
        """
        Register a listener by adding it to the event's listener list.

        When the event is posted, 
        all registered listeners associated with that event will be invoked.
        """
        self.__listeners[(event_class, channel_id)].add(listener)

    def unregister_listener(self, event_class: type[BaseEvent],
                            listener: ListenerCallback, channel_id: ChannelId | None = None):
        """
        Unregister a listener.
        """
        self.__wait_remove_listeners.append(((event_class, channel_id), listener))

    def post(self, event: BaseEvent, channel_id: ChannelId | None = None):
        """
        Invoke all registered listeners associated with the event.
        """
        if (type(event), channel_id) not in self.__listeners:
            return

        self.__read_lock += 1
        for listener in self.__listeners[(type(event), channel_id)]:
            listener(event)
        self.__read_lock -= 1

        if self.__read_lock == 0:
            for (e, c), listener in self.__wait_remove_listeners:
                try:
                    self.__listeners[(e, c)].remove(listener)
                except KeyError:
                    log_warning(f'{listener} is not listening to ({e}, {c})')

            self.__wait_remove_listeners.clear()
