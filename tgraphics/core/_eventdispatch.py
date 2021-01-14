from collections import defaultdict
from functools import partial

class _DispatcherHelper:
    def __init__(self, dispatcher):
        self._d = dispatcher

    def __call__(self, func, *, name=None):
        """
        add event handler via decorator
        """
        if isinstance(func, str):
            return partial(self.__call__, name=func)
        self[name if name else func.__name__] = func

    def __getitem__(self, name):
        class _EventHelper:
            def __init__(self, dhelper, name):
                self._dh = dhelper
                self._n = name

            def __call__(self, func):
                """
                add event handler via decorator
                """
                self._dh[self._n] = func

            @property
            def handler(self):
                try:
                    return self._dh._d._handlers[self._n]
                except KeyError:
                    return None

            @handler.setter
            def handler(self, func):
                self(func)

            def add_listener(self, listener):
                self._dh._d._listeners[self._n].append(listener)

            def remove_listener(self, listener):
                self._dh._d._listeners[self._n].remove(listener)

        return _EventHelper(self, name)

    def __setitem__(self, name, func):
        if func is not None:
            self._d._handlers[name] = func
        else:
            del self._d._handlers[name]


class EventDispatcher:
    def __init__(self):
        self._t = None
        self._handlers = dict()
        self._listeners = defaultdict(list)
        self._e_helper = _DispatcherHelper(self)

    @property
    def target(self):
        return self._t

    @target.setter
    def target(self, target):
        self._t = target

    @property
    def event(self):
        return self._e_helper

    @property
    def handlers(self):
        _h = self._t.handlers if self._t is not None else set()
        return _h | set(self._handlers.keys()) | {e for e, ls in self._listeners.items() if ls}
            
    def dispatch(self, event, *args, **kwargs):
        # comprehension is often faster
        res = any([ls(*args, **kwargs) for ls in self._listeners[event]])
        try:
            return self._handlers[event](*args, **kwargs) or res
        except KeyError:
            if self._t:
                return self._t.dispatch(event, *args, **kwargs) or res
            else:
                return res if self._listeners[event] else True
                # TODO: log?       
