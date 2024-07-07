"""
The module defines EventManager.
"""

from collections import defaultdict
from typing import Callable, Optional, TypeAlias

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
        self.listeners: defaultdict[tuple[type[BaseEvent], Optional[int]],
                                    list[ListenerCallback]] = defaultdict(list)

    def register_listener(self, event_class: type[BaseEvent], listener: ListenerCallback, channel_id: Optional[int] = None):
        """
        Register a listener by adding it to the event's listener list.

        When the event is posted, 
        all registered listeners associated with that event will be invoked.
        """
        self.listeners[(event_class, channel_id)].append(listener)

    def unregister_listener(self, event_class: type[BaseEvent],
                            listener: ListenerCallback, channel_id: int | None = None):
        """
        Unregister a listener.
        """
        try:
            self.listeners[(event_class, channel_id)].remove(listener)
        except ValueError:
            print(f'{listener} is not listening to ({event_class}, {channel_id})')

    def post(self, event: BaseEvent, channel_id: Optional[int] = None):
        """
        Invoke all registered listeners associated with the event.
        """
        if (type(event), channel_id) not in self.listeners:
            raise KeyError("The event hasn't been registered")
        for listener in self.listeners[(type(event), channel_id)]:
            listener(event)
