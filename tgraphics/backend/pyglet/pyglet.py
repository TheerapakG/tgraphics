import asyncio
import datetime
import traceback
import time

import pyglet
from pyglet.window import Window as _Window
from pyglet.gl import *

from ...core.eventdispatch import EventDispatcher, event_handler
from ...utils.typehint import *

_WindowsMap = dict() # type: Dict[Any, Window]
_Windows = set() # type: Set[Window]

class Renderer:
    def __init__(self, window):
        self._target = None
        self._window = window
        self._batch = pyglet.graphics.Batch()
        self._color = (0, 0, 0, 255)

    @property
    def target(self):
        class _TargetGetProxy:
            def __init__(self, renderer):
                self._renderer = renderer

            def get(self):
                return self._renderer._target

            def __call__(self, new_target):
                class _TargetCtxMgrProxy:
                    def __init__(self, renderer):
                        self._renderer = renderer
                        self._replacing = []

                    def __enter__(self):
                        self._replacing.append(self._target)
                        self._renderer.target = new_target

                    def __exit__(self, type, value, traceback):
                        self._renderer.target = self._replacing.pop()
                
                return _TargetCtxMgrProxy(self._renderer)

        return _TargetGetProxy(self)

    @target.setter
    def target(self, new_target):
        if runner.current_renderer is not self:
            raise NotImplementedError("This operation on inactive renderer is unsupported")
        if new_target:
            glDisable(self._target.target)
            glEnable(new_target.target)
            glBindTexture(new_target.target, new_target.id)
            glViewport(0, 0, new_target.width, new_target.height)
        else:
            glDisable(self._target)
        self._target = new_target

    @property
    def draw_color(self):
        class _ColorGetProxy:
            def __init__(self, renderer):
                self._renderer = renderer

            def get(self):
                return self._renderer._color

            def __call__(self, new_color):
                class _ColorCtxMgrProxy:
                    def __init__(self, renderer):
                        self._renderer = renderer
                        self._replacing = []

                    def __enter__(self):
                        self._replacing.append(self._renderer._color)
                        self._renderer.draw_color = new_color

                    def __exit__(self, type, value, traceback):
                        self._renderer.draw_color = self._replacing.pop()
                
                return _ColorCtxMgrProxy(self._renderer)

        return _ColorGetProxy(self)

    @draw_color.setter
    def draw_color(self, new_color):
        self._renderer._color = new_color

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def update(self):
        self._batch.draw()
        self._batch = pyglet.graphics.Batch()

    def draw_line(self, p1, p2):
        if runner.current_renderer is not self:
            raise NotImplementedError("drawing via inactive renderer is unsupported")
        pyglet.graphics.Line(p1[0], self._target.height-p1[1], p2[0], self._target.height-p2[1], color=self._color[:3], batch=self._batch).opacity = self._color[3]

    def draw_point(self, point):
        if runner.current_renderer is not self:
            raise NotImplementedError("drawing via inactive renderer is unsupported")
        raise NotImplementedError()

    def draw_rect(self, rect):
        if runner.current_renderer is not self:
            raise NotImplementedError("drawing via inactive renderer is unsupported")
        raise NotImplementedError()

    def fill_rect(self, rect):
        if runner.current_renderer is not self:
            raise NotImplementedError("drawing via inactive renderer is unsupported")
        pyglet.graphics.Rectangle(rect[0][0], self._target.height-rect[0][1], rect[1][0], self._target.height-rect[1][1], color=self._color[:3], batch=self._batch).opacity = self._color[3]

class Window(EventDispatcher):
    def __init__(self, _pyg):
        super().__init__()
        self._window = _pyg
        try:
            other = _WindowsMap[_pyg]
            self._renderer = other._renderer
        except KeyError:
            self._renderer = Renderer(self)

    @event_handler
    def on_close(self):
        self.destroy()
        if not _Windows:
            stop()

    @staticmethod
    def create(title, size, full_screen, resizable):
        _window = _Window(width=size[0], height=size[1], caption=title, fullscreen=full_screen, resizable=resizable)
        window = Window(_window)
        _WindowsMap[_window] = window
        _Windows.add(window)
        
        window._last_frame_time = None
        window._current_start_time = None
        window._current_frame_time = None
        window._draw_time = datetime.timedelta()
        window._frame_delta = None
        window._target_fps = None

        on_draw_finished_event = window.event['on_draw_finished']
        @on_draw_finished_event.add_listener
        def update_frame_metrics():
            window._last_frame_time, window._current_frame_time = window._current_frame_time, time.perf_counter()
            window._draw_time = datetime.timedelta(seconds=window._current_frame_time - window._current_start_time)
            if window._last_frame_time:
                window._frame_delta = datetime.timedelta(seconds=window._current_frame_time - window._last_frame_time)
        
        runner.current_renderer = window._renderer
        if runner.running:
            runner.tasks_set.add(asyncio.create_task(window.draw_schedule()))

        return window
    
    @staticmethod
    def get(_pyg):
        return _WindowsMap[_pyg]

    @staticmethod
    def all_windows():
        """
        [READ-ONLY] Return all windows
        """
        return _Windows

    def __hash__(self):
        return hash(self._window.id)

    def __eq__(self, other):
        if not isinstance(other, Window):
            return NotImplemented
        return self._window.id == other._window.id

    def destroy(self):
        self.dispatch('on_destroy')
        _Windows.remove(self)
        self._window.destroy()

    @property
    def title(self):
        return self._window.title

    @title.setter
    def title(self, title):
        self._window.title = title

    @property
    def resizable(self):
        return self._window.resizable

    @resizable.setter
    def resizable(self, resizable):
        self._window.resizable = resizable

    @property
    def size(self):
        return self._window.size

    @size.setter
    def size(self, size):
        self._window.size = size

    def icon(self, surface):
        self._window.set_icon(surface)

    icon = property(None, icon)

    @property
    def id(self):
        return self._window.id

    @property
    def renderer(self):
        return self._renderer

    @property
    def frame_time(self):
        try:
            return getattr(self, '_frame_delta')
        except AttributeError:
            return Window.get(self._window).frame_time

    @property
    def fps(self):
        _frame_delta = self.frame_time
        if _frame_delta is not None:
            try:
                return datetime.timedelta(seconds=1)/_frame_delta
            except ZeroDivisionError:
                return None

    @fps.setter
    def fps(self, fps):
        if hasattr(self, '_target_fps'):
            self._target_fps = fps
        else:
            Window.get(self._window).fps = fps

# Image is roughly equivalent to Surface in SDL

# Sprite is roughly equivalent to Texture in SDL

class InvalidLoopStateException(Exception):
    pass

class _EventLoop(pyglet.app.EventLoop):
    async def run_async(self):
        """Begin processing events, scheduled functions and window updates.
        This method returns when :py:attr:`has_exit` is set to True.
        Developers are discouraged from overriding this method, as the
        implementation is platform-specific.
        """
        self.has_exit = False

        from pyglet.window import Window
        Window._enable_event_queue = False

        # Dispatch pending events
        for window in pyglet.app.windows:
            window.switch_to()
            window.dispatch_pending_events()

        platform_event_loop = pyglet.app.platform_event_loop
        platform_event_loop.start()
        self.dispatch_event('on_enter')
        self.is_running = True

        while not self.has_exit:
            await asyncio.sleep(0)
            timeout = self.idle()
            platform_event_loop.step(timeout)

        self.is_running = False
        self.dispatch_event('on_exit')
        platform_event_loop.stop()

def init():
    # "fix" pygame overwriting some fonts from the same family
    pyglet.app.event_loop = _EventLoop()

class _Runner(EventDispatcher):
    running = False
    mouses = None
    _current_renderer = None
    tasks_set = set()
    cleanup_coro = list()
    GARBAGE_CLEANUP_PERIOD = 60

    _stop_event = None

    def __init__(self):
        pass

    @property
    def current_renderer(self):
        return self._current_renderer

    @current_renderer.setter
    def current_renderer(self, renderer):
        self._current_renderer = renderer
        renderer._window.switch_to()
        if renderer._target:
            glEnable(renderer._target.target)
            glBindTexture(renderer._target.target, renderer._target.id)
            glViewport(0, 0, renderer._target.width, renderer._target.height)
    
    def run(self):
        if self.running:
            raise InvalidLoopStateException()
        self.running = True
        asyncio.run(self.run_all())

    def stop(self):
        if self.running:
            self.running = False
            self._stop_event.set()
        else:
            raise InvalidLoopStateException()

    async def run_events(self):
        pyglet.clock.tick()

    async def run_coros_cleanup(self):
        while self.running:
            finished = [c for c in self.cleanup_coro if c.done()]
            self.cleanup_coro = [c for c in self.cleanup_coro if not c.done()]
            for c in finished:
                try:
                    await c
                except Exception:
                    print('Exception while cleaning up coroutine', c)
                    print(traceback.format_exc())
            try:
                await asyncio.wait_for(self._stop_event.wait(), self.GARBAGE_CLEANUP_PERIOD)
            except asyncio.TimeoutError:
                pass

    async def run_all(self):
        self._stop_event = asyncio.Event()

        for window in _Windows:
            self.tasks_set.add(asyncio.create_task(window.draw_schedule()))

        self.tasks_set.add(asyncio.create_task(self.run_events()))
        self.tasks_set.add(asyncio.create_task(self.run_coros_cleanup()))

        await self._stop_event.wait()
        for event in self.tasks_set:
            await event

    def cleanup_coro_done(self, coro):
        self.cleanup_coro.append(coro)

runner = _Runner()

def run():
    runner.run()

def stop():
    runner.stop()

def uninit():
    if runner.running:
        stop()

class InvalidRendererStateException(Exception):
    pass

def current_renderer() -> Renderer:
    if runner.current_renderer:
        return runner.current_renderer
    else:
        raise InvalidRendererStateException()

def cleanup_coro_done(coro):
    runner.cleanup_coro_done(coro)
