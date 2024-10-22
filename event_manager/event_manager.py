"""
The module defines EventManager.
"""

from collections import defaultdict
from typing import Callable, TypeAlias

from event_manager.events import BaseEvent
from util import log_critical, log_warning

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

        self.__wait_remove_listeners: dict[tuple[type[BaseEvent], ChannelId | None],
                                           list[ListenerCallback]] = defaultdict(list)
        self.__wait_add_listeners: dict[tuple[type[BaseEvent], ChannelId | None],
                                        list[ListenerCallback]] = defaultdict(list)
        self.__read_lock: dict[tuple[type[BaseEvent], ChannelId | None], int] = defaultdict(int)
        """The lock to ensure one can modify self.listeners only when no one is iterating it."""

    def register_listener(self, event_class: type[BaseEvent],
                          listener: ListenerCallback, channel_id: ChannelId | None = None):
        """
        Register a listener by adding it to the event's listener list.

        When the event is posted, 
        all registered listeners associated with that event will be invoked.
        """
        if self.__read_lock[(event_class, channel_id)] == 0:
            self.__listeners[(event_class, channel_id)].add(listener)
        elif self.__read_lock[(event_class, channel_id)] > 0:
            self.__wait_add_listeners[(event_class, channel_id)].append(listener)
        else:
            raise ValueError('the value of the read lock of event manager less than 0')

    def unregister_listener(self, event_class: type[BaseEvent],
                            listener: ListenerCallback, channel_id: ChannelId | None = None):
        """
        Unregister a listener.
        """
        if self.__read_lock[(event_class, channel_id)] == 0:
            self.__listeners[(event_class, channel_id)].remove(listener)
        elif self.__read_lock[(event_class, channel_id)] > 0:
            self.__wait_remove_listeners[(event_class, channel_id)].append(listener)
        else:
            raise ValueError('the value of the read lock of event manager less than 0')

    def post(self, event: BaseEvent, channel_id: ChannelId | None = None):
        """
        Invoke all registered listeners associated with the event.
        """
        if not isinstance(event, BaseEvent):
            log_critical(f'pass event = {event}, which is not an instance of BaseEvent')

        if (type(event), channel_id) not in self.__listeners:
            return

        self.__read_lock[(type(event), channel_id)] += 1
        for listener in self.__listeners[(type(event), channel_id)]:
            listener(event)
        self.__read_lock[(type(event), channel_id)] -= 1

        if self.__read_lock[(type(event), channel_id)] == 0:
            for listener in self.__wait_add_listeners[(type(event), channel_id)]:
                self.__listeners[(type(event), channel_id)].add(listener)
            self.__wait_add_listeners[(type(event), channel_id)].clear()

            for listener in self.__wait_remove_listeners[(type(event), channel_id)]:
                try:
                    self.__listeners[(type(event), channel_id)].remove(listener)
                except KeyError:
                    log_warning(f'try unregister {listener} which is not registered to '
                                f'({type(event)}, {channel_id})')
            self.__wait_remove_listeners[(type(event), channel_id)].clear()
