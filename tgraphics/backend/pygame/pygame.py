import asyncio
from collections import defaultdict
import datetime
from enum import Enum, IntEnum
import os
import time
import traceback

os.environ['PYGAME_FREETYPE'] = "1"
import pygame

from . import _mouse
from .key import Keys
from ._sdl2 import *
from ...core.eventdispatch import EventDispatcher, event_handler
from ...utils.typehint import *

# pylint: disable=no-member
import pygame._sdl2

_PygameFlagSdl_WINDOWPOS_UNDEFINED = getattr(pygame, "WINDOWPOS_UNDEFINED", pygame._sdl2.WINDOWPOS_UNDEFINED)
_PygameClsSdlWindow = getattr(pygame, "Window", pygame._sdl2.Window)
_PygameClsSdlRenderer = getattr(pygame, "Renderer", pygame._sdl2.Renderer)
_PygameClsSdlTexture= getattr(pygame, "Texture", pygame._sdl2.Texture)

# from https://github.com/pygame/pygame/blob/main/src_c/cython/pygame/_sdl2/video.pxd
# there's probably no any more elegant way to get these
class BlendMode(IntEnum):
    BLENDMODE_NONE = 0x00000000
    BLENDMODE_BLEND = 0x00000001
    BLENDMODE_ADD = 0x00000002
    BLENDMODE_MOD = 0x00000004
    BLENDMODE_INVALID = 0x7FFFFFFF

_WindowsMap = dict() # type: Dict[Any, Window]
if sys.platform == 'win32':
    _HWNDMap = dict() # type: Dict[int, Window]
_Windows = set() # type: Set[Window]

class Renderer:
    def __init__(self, _pyg):
        self._window, self._renderer = _pyg
        try:
            self._ctype = _WindowsMap[self._window]._renderer._ctype
        except KeyError:
            self._ctype = sdl_getrenderer(self._window._ctype)

    def __hash__(self):
        return hash(self._window.id)

    def __eq__(self, other):
        if not isinstance(other, Renderer):
            return NotImplemented
        return self._window.id == other._window.id

    @property
    def window(self):
        return self._window

    @property
    def target(self):
        class _TargetGetProxy:
            def __init__(self, renderer):
                self._renderer = renderer

            def get(self):
                return self._renderer._renderer.target

            def __call__(self, new_target):
                class _TargetCtxMgrProxy:
                    def __init__(self, renderer):
                        self._renderer = renderer
                        self._replacing = []

                    def __enter__(self):
                        self._replacing.append(Texture((self._renderer, self._renderer._renderer.target)))
                        self._renderer.target = new_target

                    def __exit__(self, type, value, traceback):
                        self._renderer.target = self._replacing.pop()
                
                return _TargetCtxMgrProxy(self._renderer)

        return _TargetGetProxy(self)

    @target.setter
    def target(self, new_target):
        if new_target:
            self._renderer.target = new_target._texture
        else:
            self._renderer.target = None

    @property
    def draw_color(self):
        class _ColorGetProxy:
            def __init__(self, renderer):
                self._renderer = renderer

            def get(self):
                return self._renderer._renderer.draw_color

            def __call__(self, new_color):
                class _ColorCtxMgrProxy:
                    def __init__(self, renderer):
                        self._renderer = renderer
                        self._replacing = []

                    def __enter__(self):
                        self._replacing.append(self._renderer._renderer.draw_color)
                        self._renderer.draw_color = new_color

                    def __exit__(self, type, value, traceback):
                        self._renderer.draw_color = self._replacing.pop()
                
                return _ColorCtxMgrProxy(self._renderer)

        return _ColorGetProxy(self)

    @draw_color.setter
    def draw_color(self, new_color):
        self._renderer.draw_color = new_color
        if new_color[3] < 255:
            sdl_setrenderdrawblendmode(self._ctype, BlendMode.BLENDMODE_BLEND)
        else:
            sdl_setrenderdrawblendmode(self._ctype, BlendMode.BLENDMODE_NONE)

    def clear(self):
        with self.draw_color((0, 0, 0, 255)):
            self._renderer.clear()

    def update(self):
        self._renderer.present()

    def draw_line(self, p1, p2):
        self._renderer.draw_line(p1, p2)

    def draw_point(self, point):
        self._renderer.draw_point(point)

    def draw_rect(self, rect):
        self._renderer.draw_rect(rect)

    def fill_rect(self, rect):
        self._renderer.fill_rect(rect)

class Window(EventDispatcher):
    def __init__(self, _pyg):
        super().__init__()
        self._window = _pyg
        try:
            other = _WindowsMap[_pyg]
            self._ctype = other._ctype
            self._renderer = other._renderer
            self._funcs = other._funcs
        except KeyError:
            self._ctype = sdl_getwindowfromid(self._window.id)
            try:
                self._renderer = Renderer((self, _PygameClsSdlRenderer.from_window(self._window)))
            except pygame._sdl2.sdl2.error:
                self._renderer = Renderer((self, _PygameClsSdlRenderer(self._window, target_texture=True)))
            self._funcs = defaultdict(lambda: None)

    @event_handler
    def on_close(self):
        self.destroy()
        if not _Windows:
            stop()

    @staticmethod
    def create(title, size, full_screen, resizable):
        _window = _PygameClsSdlWindow(title, size, fullscreen=full_screen, resizable=resizable)
        window = Window(_window)
        _WindowsMap[_window] = window
        if sys.platform == 'win32':
            info = sdl_getwindowwminfo(window._ctype)
            if info.subsystem == SDL_SYSWM_WINDOWS:
                _HWNDMap[int(info.info.win.window)] = window
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

        if sys.platform == 'win32':
            import ctypes
            from ctypes.wintypes import DWORD, HWND, UINT
            user32 = ctypes.windll.user32
            TIMERPROC = ctypes.WINFUNCTYPE(None, HWND, UINT, ctypes.POINTER(UINT), DWORD)
            window._blocking = False

            def timed_func(hwnd, msg, timer, t):
                if window._blocking and window in _Windows:
                    window.dispatch('on_draw')
                    target_period = (datetime.timedelta(seconds=1)/window._target_fps)
                    compensated_period = max(0, int((target_period-window._frame_delta).total_seconds() * 1000))
                    user32.SetTimer(0, window._timer, ctypes.c_uint(compensated_period), window._timed_func)
                else:
                    user32.SetTimer(0, window._timer, 0x7fffffff, window._timed_func)

            window._timed_func = TIMERPROC(timed_func)
            window._timer = user32.SetTimer(0, 0, 0x7fffffff, window._timed_func)

            on_syswm = window.event['on_syswm']
            @on_syswm.add_listener
            def on_syswm(_msg):
                blocking = False
                unblocking = False
                msg = int(_msg.msg.win.msg)
                wparam = int(_msg.msg.win.wParam)
                lparam = int(_msg.msg.win.lParam)

                if msg == 274: # WM_SYSCOMMAND
                    if wparam == 61696 and lparam & (1 >> 16) <= 0: # wparam == SC_KEYMENU
                        return # no menu
                    if wparam & 0xfff0 in (61456, 61440): # wparam in SC_MOVE, SC_Size
                        # Before WM_ENTERSIZEMOVE, https://docs.microsoft.com/en-us/windows/win32/winmsg/wm-entersizemove
                        blocking = True
                elif msg == 562: # WM_EXITSIZEMOVE
                    unblocking = True

                if blocking:
                    window._blocking = True
                    target_period = (datetime.timedelta(seconds=1)/window._target_fps)
                    compensated_period = max(0, int((target_period-window._frame_delta).total_seconds() * 1000))
                    user32.SetTimer(0, window._timer, ctypes.c_uint(compensated_period), window._timed_func)
                elif unblocking:
                    window._blocking = False
        
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

    async def draw_schedule(self):
        while runner.running:
            if self not in _Windows:
                break
            renderer = self.renderer
            renderer.target = None
            renderer.clear()
            self._current_start_time = time.perf_counter()
            if self._target_fps and self._current_frame_time:
                target_time = datetime.timedelta(seconds=1) / self._target_fps
                expect_time = datetime.timedelta(seconds=self._current_start_time - self._current_frame_time) + self._draw_time
                await asyncio.sleep((target_time-expect_time).total_seconds())
            runner.current_renderer = renderer
            self.dispatch('on_draw')
            renderer.update()
            await asyncio.sleep(0)


class Surface:
    def __init__(self, _pyg):
        self._surface = _pyg

    @staticmethod
    def create(size):
        return Surface(pygame.Surface(size))

    @property
    def w(self):
        return self._surface.get_width()

    @property
    def h(self):
        return self._surface.get_height()

    @property
    def size(self):
        return self._surface.get_size()

    def subsurface(self, rect):
        return Surface(self._surface.subsurface(rect))
        
    def blit_from(self, src, dst_coord, src_rect=None):
        """
        blit `src` (or a portion of it if `src_rect` is specified) onto this surface at `dst_coord`.
        
        parameters:
            src: Surface
                surface to blit from
            dst_coord
                coordinate to blit to
            [src_rect]
                rect to blit from, blit the entire `src` if unspecified
        """
        self._surface.blit(src._surface, dst_coord, src_rect, pygame.BLEND_ALPHA_SDL2)

    def blit_to(self, dst, dst_coord, src_rect=None):
        """
        blit this surface (or a portion of it if `src_rect` is specified) onto `dst` at `dst_coord`.\n
        equivalent to `dst.blit_from(self, dst_coord, src_rect)`
        
        parameters:
            dst: Surface
                surface to blit to
            dst_coord
                coordinate to blit to
            [src_rect]
                rect to blit from, blit the entire `src` if unspecified
        """
        dst.blit_from(self, dst_coord, src_rect)

    def has_alpha(self):
        return bool(self._surface.get_flags() & pygame.SRCALPHA)

    def convert_as_format(self, target_surface):
        return Surface(self._surface.convert(target_surface._surface))

    def convert_as_alpha_format(self, target_surface):
        return Surface(self._surface.convert_alpha(target_surface._surface))

    @staticmethod
    def _from_foreign(file_or_io, optional_ext_hint=""):
        return Surface(pygame.image.load(file_or_io, optional_ext_hint))

    @staticmethod
    def from_file(filename):
        return Surface._from_foreign(filename)

    @staticmethod
    def from_io(io, ext_hint):
        return Surface._from_foreign(io, ext_hint)

    @staticmethod
    def from_str(string, size, format):
        return Surface(pygame.image.fromstring(string, size, format))


# reimplementation of SDL_TextureAccess enum as pygame does not expose it
class TextureAccessEnum(Enum):
    Static = 0
    Streaming = 1
    Target = 2


class Texture:
    def __init__(self, _pyg=None):
        self._renderer, self._texture = _pyg

    @staticmethod
    def create(renderer: Renderer, size, access: TextureAccessEnum=TextureAccessEnum.Static, blend=None):
        if access == TextureAccessEnum.Static:
            _n_dict = {'static': True}
        elif access == TextureAccessEnum.Streaming:
            _n_dict = {'streaming': True}
        elif access == TextureAccessEnum.Target:
            _n_dict = {'target': True}
        else:
            raise ValueError('unknown access enum value')

        tex = Texture((renderer, _PygameClsSdlTexture(renderer._renderer, size, **_n_dict)))

        if blend:
            tex.blend_mode = blend

        return tex

    @staticmethod
    def create_as_target(renderer: Renderer, size, blend=None):
        return Texture.create(renderer, size, TextureAccessEnum.Target, blend)

    @staticmethod
    def from_surface(renderer: Renderer, surface: Surface):
        return Texture((renderer, _PygameClsSdlTexture.from_surface(renderer._renderer, surface._surface)))

    @staticmethod
    def from_file(renderer: Renderer, filename):
        return Texture.from_surface(renderer, Surface.from_file(filename))

    @staticmethod
    def from_io(renderer: Renderer, io, ext_hint):
        return Texture.from_surface(renderer, Surface.from_io(io, ext_hint))

    @staticmethod
    def from_str(renderer: Renderer, string, size, format):
        return Texture.from_surface(renderer, Surface.from_str(string, size, format))

    @property
    def w(self):
        return self._texture.width

    @property
    def h(self):
        return self._texture.height

    @property
    def size(self):
        return self.w, self.h

    @property
    def blend_mode(self):
        return BlendMode(self._texture.blend_mode)

    @blend_mode.setter
    def blend_mode(self, blend):
        self._texture.blend_mode = int(blend)

    @property
    def renderer(self):
        return self._renderer

    def blit_to_target(self, src_rect=None, dst_rect_or_coord=None, angle=0, origin=None, flipX=False, flipY=False):
        """
        copy this texture (or a portion of it if `src_coord` is specified) to the rendering target.
        
        parameters:
            [src_rect]
                rect to blit from, blit the entire `src` if unspecified
            [dst_rect_or_coord]
                rect or coord to blit to, blit to the entire target if unspecified
            [angle]
                angle (in degrees) to rotate dst_rect (clockwise)
            [origin]
                point around which dst_rect will be rotated
                if None, it will be equal to the center: (dstrect.w/2, dstrect.h/2)
            [flipX]
                flip horizontally
            [flipY]
                flip vertically
        """
        self._texture.draw(src_rect, dst_rect_or_coord, angle, origin, flipX, flipY)

    def draw(self, location, size=None):
        if size:
            raise NotImplementedError()
        else:
            self.blit_to_target(dst_rect_or_coord=location)

    def as_color_mod(self, color):
        _orig_col = (self._texture.color, self._texture.alpha, self._texture.blend_mode)
        self._texture.color = color[0:3]
        blend = _orig_col[2]
        if len(color) > 3:
            self._texture.alpha = color[3]
            self._texture.blend_mode = BlendMode.BLENDMODE_NONE
            if _orig_col[2] == BlendMode.BLENDMODE_NONE:
                blend = BlendMode.BLENDMODE_BLEND

        new_tex = Texture.create(self._renderer, self.size, TextureAccessEnum.Target, blend=blend)

        with self._renderer.target(new_tex):
            self.blit_to_target()
        
        self._texture.color = _orig_col[0]
        self._texture.alpha = _orig_col[1]
        self._texture.blend_mode = _orig_col[2]

        return new_tex

    def as_size(self, size):
        new_tex = Texture.create(self._renderer, size, TextureAccessEnum.Target)

        with self._renderer.target(new_tex):
            self.blit_to_target()

        return new_tex


def _parse_font_entry_win(name, font, fonts):
    """
    Parse out a simpler name and the font style from the initial file name.

    :param name: The font name
    :param font: The font file path
    :param fonts: The pygame font dictionary

    :return: Tuple of (bold, italic, name)
    """
    true_type_suffix = '(TrueType)'
    # mods = ('demibold', 'narrow', 'light', 'unicode', 'bt', 'mt')
    if name.endswith(true_type_suffix):
        name = name.rstrip(true_type_suffix).rstrip()
    name = name.lower().split()
    bold = italic = 0
    # for mod in mods:
    #     if mod in name:
    #         name.remove(mod)
    if 'bold' in name:
        name.remove('bold')
        bold = 1
    if 'italic' in name:
        name.remove('italic')
        italic = 1
    name = ''.join(name)
    name = pygame.sysfont._simplename(name)

    pygame.sysfont._addfont(name, bold, italic, font, fonts)

def init():
    # "fix" pygame overwriting some fonts from the same family
    pygame.sysfont._parse_font_entry_win = _parse_font_entry_win
    pygame.init()
    sdl_eventstate(pygame.SYSWMEVENT, 1)

class InvalidLoopStateException(Exception):
    pass

class _Runner(EventDispatcher):
    running = False
    mouses = None
    current_renderer = None
    tasks_set = set()
    cleanup_coro = list()
    GARBAGE_CLEANUP_PERIOD = 60

    _stop_event = None

    def __init__(self):
        pass
    
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

    async def run_one_event(self, event):
        _window = getattr(event, 'window', None)
        if _window:
            window = Window.get(_window)
            self.current_renderer = window.renderer
        else:
            window = None

        # TODO: LoOkUp FuNcTiOnS!?!
        if event.type == pygame.QUIT:
            self.running = False
            return
        elif event.type == pygame.KEYDOWN:
            try:
                key = Keys(event.key)
            except ValueError:
                key = event.key
            try:
                mod = Keys(event.mod)
            except ValueError:
                mod = event.mod
            await window.dispatch_async('on_key_press', key, mod)
        elif event.type == pygame.KEYUP:
            try:
                key = Keys(event.key)
            except ValueError:
                key = event.key
            try:
                mod = Keys(event.mod)
            except ValueError:
                mod = event.mod
            await window.dispatch_async('on_key_release', key, mod)
        elif event.type == pygame.MOUSEMOTION:
            self.mouses = _mouse._mouse_from_pygtpl(event.buttons)
            if self.mouses != _mouse.NButton:
                await window.dispatch_async('on_mouse_drag', *event.pos, *event.rel, self.mouses)
            else:
                await window.dispatch_async('on_mouse_motion', *event.pos, *event.rel)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == pygame.BUTTON_WHEELDOWN or event.button == pygame.BUTTON_WHEELUP:
                return
            button = _mouse._mouse_from_pyg(event.button)
            self.mouses &= ~button
            last = False
            if self.mouses == _mouse.NButton:
                sdl_capturemouse(False)
                last = True
            await window.dispatch_async('on_mouse_release', *event.pos, button, pygame.key.get_mods(), last=last)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_WHEELDOWN or event.button == pygame.BUTTON_WHEELUP:
                return
            button = _mouse._mouse_from_pyg(event.button)
            first = False
            if self.mouses == _mouse.NButton:
                sdl_capturemouse(True)
                first = True
            self.mouses |= button
            await window.dispatch_async('on_mouse_press', *event.pos, button, pygame.key.get_mods(), first=first)
        elif event.type == pygame.MOUSEWHEEL:
            if event.flipped:
                dx = -event.x
                dy = -event.y
            else:
                dx = event.x
                dy = event.y

            await window.dispatch_async('on_mouse_scroll', *pygame.mouse.get_pos(), dx, dy)
        
        elif event.type == pygame.WINDOWCLOSE:
            await window.dispatch_async('on_close')
        elif event.type == pygame.WINDOWENTER:
            await window.dispatch_async('on_mouse_enter')
        elif event.type == pygame.WINDOWLEAVE:
            await window.dispatch_async('on_mouse_leave')
        elif event.type == pygame.WINDOWHIDDEN:
            await window.dispatch_async('on_hide')
        elif event.type == pygame.WINDOWMOVED:
            await window.dispatch_async('on_move', -1, -1)
        elif event.type == pygame.WINDOWRESIZED:
            await window.dispatch_async('on_resize', -1, -1)
        elif event.type == pygame.WINDOWSHOWN:
            await window.dispatch_async('on_show', -1, -1)
        elif event.type == pygame.WINDOWMINIMIZED:
            await window.dispatch_async('on_minimized')
        elif event.type == pygame.WINDOWMAXIMIZED:
            await window.dispatch_async('on_maximized')
        elif event.type == pygame.WINDOWRESTORED:
            await window.dispatch_async('on_restored')
        elif event.type == pygame.WINDOWFOCUSGAINED:
            await window.dispatch_async('on_gain_focus')
        elif event.type == pygame.WINDOWFOCUSLOST:
            await window.dispatch_async('on_lost_focus')
        elif event.type == pygame.WINDOWTAKEFOCUS:
            await window.dispatch_async('on_offered_focus')
        elif event.type == pygame.WINDOWHITTEST:
            await window.dispatch_async('on_hit_test')

    async def run_events(self):
        def _immediate_event(userdata, event: ctypes.POINTER(SDL_Event)):
            if event.contents.type == SDL_SYSWMEVENT:
                msg = event.contents.syswm.msg.contents
                if msg.subsystem == SDL_SYSWM_WINDOWS:
                    hwnd = msg.msg.win.hwnd
                    window = _HWNDMap[hwnd]
                    window.dispatch('on_syswm', msg)
                else:
                    print('unknown WM')
            return 1

        event_filt = SDL_EventFilter(_immediate_event)

        sdl_addeventwatch(event_filt, None)

        pygame.event.clear()
        _mouse._mouse_from_pygtpl(pygame.mouse.get_pressed(5))

        current_loop_time = None
        loop_run_time = datetime.timedelta()

        while self.running:
            current_start_time = time.perf_counter()
            if not current_loop_time or any(not w._target_fps for w in _Windows):
                await asyncio.sleep(0)
            else:
                target_time = datetime.timedelta(seconds=1) / max(w._target_fps for w in _Windows)
                expect_time = datetime.timedelta(seconds=current_start_time - current_loop_time) + loop_run_time
                await asyncio.sleep((target_time-expect_time).total_seconds()/2)

            events = pygame.event.get(pump=False)
            filtered_events = [e for e in events if e.type != pygame.SYSWMEVENT]
            for event in filtered_events:
                if not self.running:
                    return
                try:
                    await self.run_one_event(event)
                except Exception:
                    print('Exception while dispatching event', event)
                    print(traceback.format_exc())
            
            current_loop_time = time.perf_counter()
            loop_run_time = datetime.timedelta(seconds=current_loop_time - current_start_time)
            pygame.event.pump()
            
            # TODO: if not in "hog cpu" context (another thing to do) then yield to other process
            # until before next frame is needed, then we just await asyncio.sleep(0) at the start of this loop

        sdl_deleventwatch(event_filt, None)

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
    pygame.quit()

class InvalidRendererStateException(Exception):
    pass

def current_renderer() -> Renderer:
    if runner.current_renderer:
        return runner.current_renderer
    else:
        raise InvalidRendererStateException()

def cleanup_coro_done(coro):
    runner.cleanup_coro_done(coro)
