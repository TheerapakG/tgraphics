from abc import ABCMeta
from collections import defaultdict
from functools import partial
import traceback
from types import MethodType

from ..utils.typehint import *
from ..utils.asynchelper import *

class ListenerNotExistError(Exception):
    def __init__(self, event, listener, element) -> None:
        super().__init__('listener {} for event `{}` does not exist in {}'.format(listener, event, element))
        self.listener = listener
        self.event = event
        self.element = element


class EventHandler:
    def __init__(self, event, func) -> None:
        self.event = event
        self.func = func


def event_handler(func, *, name=None):
    """
    add event handler via decorator relying on the metaclass
    """
    if isinstance(func, str):
        return partial(event_handler, name=func)
    return EventHandler(name if name else func.__name__, func)

def _invoke(f, *args, _event, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as e:
        print('Exception while dispatching event listener', _event)
        print(traceback.format_exc())
        return False

async def _invoke_async(f, *args, _event, **kwargs):
    try:
        return await invoke(f, *args, **kwargs)
    except Exception as e:
        print('Exception while dispatching event listener', _event)
        print(traceback.format_exc())
        return False

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
        found = False
        res = False
        for cls in anchor.__mro__:
            if self._listeners[cls][event]:
                res = any([_invoke(f, *args, _event=event, **kwargs) for f in self._listeners[cls][event].copy()]) or res
            if self._handlers[cls][event]:
                found = True
                res = self._handlers[cls][event](*args, **kwargs)
            if found:
                return res

        if self._target:
            return self._target.dispatch(event, *args, **kwargs) or res
            
        return True

    async def dispatch_async_from_anchor(self, anchor, event, *args, **kwargs):
        found = False
        res = False
        for cls in anchor.__mro__:
            if self._listeners[cls][event]:
                res = any([await _invoke_async(f, *args, _event=event, **kwargs) for f in self._listeners[cls][event].copy()]) or res
            if self._handlers[cls][event]:
                found = True
                res = await invoke(self._handlers[cls][event], *args, **kwargs)
            if found:
                return res

        if self._target:
            return (await self._target.dispatch_async(event, *args, **kwargs)) or res
            
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


class HandlersDescriptor:
    def __init__(self, cls) -> None:
        self.cls = cls
        
    def __get__(self, obj, cls):
        return obj._handlers(self.cls)


class EventDescriptor:
    def __init__(self, cls) -> None:
        self.cls = cls

    def __get__(self, obj, cls):
        return obj._event(self.cls)


class DispatchDescriptor:
    def __init__(self, cls) -> None:
        self.cls = cls
        
    def __get__(self, obj, cls):
        return partial(obj._dispatch, self.cls)


class DispatchAsyncDescriptor:
    def __init__(self, cls) -> None:
        self.cls = cls
        
    def __get__(self, obj, cls):
        return partial(obj._dispatch_async, self.cls)


class EventDispatcherMetaMixin:
    """
    metaclass to make `.event` and `.dispatch`es of EventDispatcher work with super()
    """
    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)
        self._instantiated_handlers = [e for e in attrs.values() if isinstance(e, EventHandler)]
        self.handlers = HandlersDescriptor(self)
        self.event = EventDescriptor(self)
        self.dispatch = DispatchDescriptor(self)
        self.dispatch_async = DispatchAsyncDescriptor(self)

    @classmethod
    def composite_with(cls, other_cls):
        class EventDispatcherCompositeMeta(cls, other_cls):
            @classmethod
            def get_base(this_cls):
                class EventDispatcherCompositeBase(metaclass=this_cls):
                    handlers: Set[str]
                    event: EventInstanceProxy
                    dispatch: Callable[..., bool]
                    dispatch_async: Callable[..., Coroutine[None, None, bool]]

                    _instantiated_handlers: List[EventHandler]

                    def __init__(self, *args, **kwargs):
                        self._lookup_helper = EventLookupHelper(self)
                        for cls in type(self).__mro__:
                            _handlers = getattr(cls, '_instantiated_handlers', None)
                            if _handlers:
                                for e in _handlers:
                                    self._event(cls)[e.event](MethodType(e.func, self))
                        super().__init__(*args, **kwargs)

                    @property
                    def target(self):
                        return self._lookup_helper.target

                    @target.setter
                    def target(self, target):
                        self._lookup_helper.target = target

                    def _handlers(self, anchor) -> Set[str]:
                        return self._lookup_helper.handlers_from_anchor(anchor)

                    def _event(self, anchor) -> EventInstanceProxy:
                        return self._lookup_helper.proxy_from_anchor(anchor)

                    def _dispatch(self, anchor, event, *args, **kwargs) -> bool:
                        return self._lookup_helper.dispatch_from_anchor(anchor, event, *args, **kwargs)

                    async def _dispatch_async(self, anchor, event, *args, **kwargs) -> bool:
                        return await self._lookup_helper.dispatch_async_from_anchor(anchor, event, *args, **kwargs)

                return EventDispatcherCompositeBase

        return EventDispatcherCompositeMeta


EventDispatcherMeta = EventDispatcherMetaMixin.composite_with(type)
EventDispatcherABCMeta = EventDispatcherMetaMixin.composite_with(ABCMeta)

EventDispatcher = EventDispatcherMeta.get_base()
EventDispatcherABC = EventDispatcherABCMeta.get_base()
