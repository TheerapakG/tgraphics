from abc import ABCMeta
from collections import defaultdict

from ..utils.typehint import *

class ListenerNotExistError(Exception):
    def __init__(self, event, listener, element) -> None:
        super().__init__('listener {} for event `{}` does not exist in {}'.format(listener, event, element))
        self.listener = listener
        self.event = event
        self.element = element


class EventLookupHelper:
    def __init__(self, dispatcher):
        self._obj = dispatcher
        self._handlers = defaultdict(lambda: defaultdict(lambda: None))
        self._listeners = defaultdict(lambda: defaultdict(list))
        self._target = None

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    def handlers_from_anchor(self, anchor):
        _h = self._target.handlers if self._target is not None else set()
        e_f_pair = ((e, f) for cls in anchor.__mro__ for e, f in self._handlers[cls].items())
        return _h | {e for e, f in e_f_pair if f} | {e for e, ls in self._listeners.items() if ls}

    def proxy_from_anchor(self, anchor):
        return EventInstanceProxy(self, anchor)

    def dispatch_from_anchor(self, anchor, event, *args, **kwargs):
        res = False
        for cls in anchor.__mro__:
            found = False
            if self._listeners[cls][event]:
                res = any([f(*args, **kwargs) for f in self._listeners[cls][event]]) or res
            if self._handlers[cls][event]:
                found = True
                res = self._handlers[cls][event](*args, **kwargs) or res
            if found:
                return res

        if self._target:
            return self._target.dispatch(event, *args, **kwargs) or res
            
        return True

class EventInstanceProxy:
    def __init__(self, lookup: EventLookupHelper, anchor):
        self._lookup = lookup
        self._anchor = anchor

    def __call__(self, func, *, name=None):
        """
        add event handler via decorator
        """
        if isinstance(func, str):
            return EventTypeProxy(self, func)
        self[name if name else func.__name__] = func

    def __getitem__(self, name):
        """
        add event handler/listener with chaining support
        """
        return EventTypeProxy(self, name)

    def __setitem__(self, name, func):
        EventTypeProxy(self, name).handler = func


class EventTypeProxy:
    def __init__(self, instance_proxy: EventInstanceProxy, name):
        self._instance_proxy = instance_proxy
        self._name = name

    def __call__(self, func):
        """
        add event handler
        """
        proxy = self._instance_proxy
        proxy._lookup._handlers[proxy._anchor][self._name] = func
        return proxy._lookup._obj

    @property
    def handler(self):
        proxy = self._instance_proxy
        return proxy._lookup._handlers[proxy._anchor][self._name]

    @handler.setter
    def handler(self, func):
        self(func)

    def add_listener(self, listener):
        proxy = self._instance_proxy
        proxy._lookup._listeners[proxy._anchor][self._name].append(listener)
        return proxy._lookup._obj

    def remove_listener(self, listener):
        proxy = self._instance_proxy
        try:
            proxy._lookup._listeners[proxy._anchor][self._name].remove(listener)
            return proxy._lookup._obj
        except ValueError:
            raise ListenerNotExistError(self._name, listener, proxy._lookup._obj) from None


class EventDispatcherMetaMixin:
    """
    metaclass to make .event of EventDispatcher works with super()
    """
    def __new__(cls, clsname, bases, attrs):
        attrs['handlers'] = property(lambda self: self._handlers(type(self)))
        attrs['event'] = property(lambda self: self._event(type(self)))
        attrs['dispatch'] = lambda self, event, *args, **kwargs: self._dispatch(type(self), event, *args, **kwargs)
        return super(EventDispatcherMetaMixin, cls).__new__(cls, clsname, bases, attrs)

    @classmethod
    def composite_with(cls, other_cls):
        class EventDispatcherCompositeMeta(cls, other_cls):
            def __new__(this_cls, clsname, bases, attrs):
                return super(EventDispatcherCompositeMeta, this_cls).__new__(this_cls, clsname, bases, attrs)

            @classmethod
            def get_base(this_cls):
                class EventDispatcherCompositeBase(metaclass=this_cls):
                    event: EventInstanceProxy
                    dispatch: Callable[..., bool]

                    def __init__(self):
                        self._lookup_helper = EventLookupHelper(self)

                    @property
                    def target(self):
                        return self._lookup_helper.target

                    @target.setter
                    def target(self, target):
                        self._lookup_helper.target = target

                    def _handlers(self, anchor):
                        return self._lookup_helper.handlers_from_anchor(anchor)

                    def _event(self, anchor) -> EventInstanceProxy:
                        return self._lookup_helper.proxy_from_anchor(anchor)

                    def _dispatch(self, anchor, event, *args, **kwargs) -> bool:
                        return self._lookup_helper.dispatch_from_anchor(anchor, event, *args, **kwargs)

                return EventDispatcherCompositeBase

        return EventDispatcherCompositeMeta


EventDispatcherMeta = EventDispatcherMetaMixin.composite_with(type)
EventDispatcherABCMeta = EventDispatcherMetaMixin.composite_with(ABCMeta)

EventDispatcher = EventDispatcherMeta.get_base()
EventDispatcherABC = EventDispatcherABCMeta.get_base()
