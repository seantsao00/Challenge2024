"""
The module define EventManager.
"""

from typing import Callable, TypeAlias

from event_manager.events import BaseEvent

# The type of callback function listeners use
# It is a function accept one "Class" parameter which is subclass of BaseEvent and return None
ListenerCallback: TypeAlias = Callable[[type[BaseEvent]], None]


class EventManager:
    """
    Manager of all events and their callback function.

    The object coordinates the model, view, and controller.

    To be precise, a listener is registered by providing a specific event and a callback function.
    When the event is actually posted, all callback function bound to that event will be executed.
    """

    def __init__(self):
        self.listeners: dict[type[BaseEvent], list[ListenerCallback]] = {}

    def register_listener(self, event_class: type[BaseEvent], listener: ListenerCallback):
        """
        Register a listener by adding it to the event's listener list.

        When the event is posted, 
        all registered listeners associated with that event will be invoked.
        """
        if event_class not in self.listeners:
            self.listeners[event_class] = []
        self.listeners[event_class].append(listener)

    def post(self, event: BaseEvent):
        """
        Invoke all registered listeners associated with the event.
        """
        if type(event) not in self.listeners:
            return
        for listener in self.listeners[type(event)]:
            listener(event)
