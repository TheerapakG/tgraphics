from functools import partial

class EventDispatcher:
    def __init__(self):
        self._t = None
        self._handlers = dict()

    @property
    def target(self):
        return self._t

    @target.setter
    def target(self, target):
        self._t = target

    def event(self, func, *, name=None):
        if isinstance(func, str):
            return partial(self.event, name=func)
        if func is not None:
            self._handlers[name if name else func.__name__] = func
        else:
            del self._handlers[name]

    @property
    def handlers(self):
        _h = self._t.handlers if self._t is not None else set()
        return _h | set(self._handlers.keys())
            
    def dispatch(self, event, *args, **kwargs):
        try:
            return self._handlers[event](*args, **kwargs)
        except KeyError:
            if self._t:
                return self._t.dispatch(event, *args, **kwargs)
            else:
                # TODO: log?
                pass         
