from collections import defaultdict
from functools import partial
from typing import Generic, Optional, Type, TypeVar

class ListenerNotExistError(Exception):
    def __init__(self, event, listener, element) -> None:
        super().__init__('listener {} for event `{}` does not exist in {}'.format(listener, event, element))
        self.listener = listener
        self.event = event
        self.element = element


class EventLookupHelper:
    pass


class EventDispatcherMeta(type):
    """
    metaclass to make .event of EventDispatcher works with super()
    """
    def __new__(cls, clsname, bases, attrs):
        if 'event' in attrs:
            attrs['_event'] = attrs['event']
        attrs['event'] = lambda self, *args, **kwargs: super(type(self), self)._event(anchor=type(self))
        return super(EventDispatcherMeta, cls).__new__(cls, clsname, bases, attrs)


class EventDispatcherBase(metaclass=EventDispatcherMeta):
    event: EventLookupHelper


class EventDispatcher:
    def __init__(self):
        self._lookup_helper = EventLookupHelper(self)
        