"""
The module defines EventManager.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Callable, Optional, TypeAlias

if TYPE_CHECKING:
    from event_manager.events import BaseEvent
    ListenerCallback: TypeAlias = Callable[[BaseEvent], None]
    """
    The type of callback function used by listeners.

    It is a function accepts one "Class" parameter,
    which is a subclass of BaseEvent, and returns None
    """


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
        self.__listeners: defaultdict[tuple[type[BaseEvent], Optional[int]],
                                      list[ListenerCallback]] = defaultdict(list)
        self.__events: set[type[BaseEvent]] = set()
        """Events that have listeners."""
        self.__permanent_event: set[type[BaseEvent]] = set()
        """Events that their listener lists won't be emptied when reset_manager is invoked."""

    def register_listener(self, event_class: type[BaseEvent], listener: ListenerCallback, channel_id: Optional[int] = None):
        """
        Register a listener by adding it to the event's listener list.

        When the event is posted, 
        all registered listeners associated with that event will be invoked.
        """
        if event_class in self.__permanent_event:
            raise KeyError('Try to add a listener to a permanent event.')
        self.__listeners[(event_class, channel_id)].append(listener)
        self.__events.add(event_class)

    def unregister_listener(self, event_class: type[BaseEvent], listener: ListenerCallback, channel_id: Optional[int] = None):
        """
        Unregister a listener.
        """
        try:
            self.__listeners[(event_class, channel_id)].remove(listener)
        except ValueError:
            print('{} is not listening to ({}, {})'.format(listener, event_class, channel_id))

    def register_permanent_event(self, event_class: type[BaseEvent]):
        """
        Register an event so that its listener list won't be emptied when reset_manager is invoked.
        The event should not be listened by any listener before this operation.
        """
        if event_class in self.__permanent_event:
            raise KeyError('The event has been registered as permanent event.')
        if event_class in self.__events:
            raise KeyError('The event has been listened.')
        self.__permanent_event.add(event_class)
        self.__events.add(event_class)

    def register_permanent_listener(self, event_class: type[BaseEvent], listener: ListenerCallback, channel_id: Optional[int] = None):
        """
        Register a listener by adding it to the event's listener list.
        The event should be added into permanent event before hand.
        """
        if event_class not in self.__permanent_event:
            raise KeyError('The event should be added to permanent event before hand')
        self.__listeners[(event_class, channel_id)].append(listener)
        self.__events.add(event_class)

    def reset_manager(self):
        """
        Unregister all listeners expect listeners for events in permanent_event.
        """
        self.__listeners = {key: val
                            for key, val in self.__listeners.items() if key[0] in self.__permanent_event}

    def post(self, event: BaseEvent, channel_id: Optional[int] = None):
        """
        Invoke all registered listeners associated with the event.
        """
        if (type(event), channel_id) not in self.__listeners:
            return
        for listener in self.__listeners[(type(event), channel_id)]:
            listener(event)
