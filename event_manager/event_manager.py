"""
The module defines EventManager.
"""

from collections import defaultdict
from typing import Callable, TypeAlias

from event_manager import BaseEvent

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
    """

    def __init__(self):
        self.listeners: defaultdict[type[BaseEvent], list[ListenerCallback]] = defaultdict(list)

    def register_listener(self, event_class: type[BaseEvent], listener: ListenerCallback):
        """
        Register a listener by adding it to the event's listener list.

        When the event is posted, 
        all registered listeners associated with that event will be invoked.
        """
        self.listeners[event_class].append(listener)

    def post(self, event: BaseEvent):
        """
        Invoke all registered listeners associated with the event.
        """
        if type(event) not in self.listeners:
            return
        for listener in self.listeners[type(event)]:
            listener(event)
