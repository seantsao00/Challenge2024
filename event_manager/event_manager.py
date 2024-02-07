from typing import Type


class BaseEvent:
    """
    The superclass of all events.
    """
    name = 'Generic event'

    def __init__(self):
        pass

    def __str__(self):
        # For Debug
        return self.name


class EventManager:
    """
    It coordinates communication between the model, view, and controller.

    Each of these components, namely the Model, View, and Controller,
    acts as a listener,
    and events are broadcasted to them by the event_manager via the post() method.
    """

    def __init__(self):
        self.listeners = dict()

    def register_listener(self, event_class: type[BaseEvent], listener: function):
        """
        Register a listener by adding it to the event's listener list.

        When the event is posted, all registered listeners associated
        with that event will be invoked.
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
