import asyncio
from collections import defaultdict
from enum import Enum, IntEnum
import os

os.environ['PYGAME_FREETYPE'] = "1"
import pygame

from . import _mouse
from .key import Keys
from ._sdl2 import *
from ...core.eventdispatch import EventDispatcher

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

_WindowsMap = dict()
_Windows = set()

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

_window_create_event = None
_window_create = list()
_window_destroy_event = None
_window_destroy = list()

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

    @staticmethod
    def create(title, size, full_screen, resizable):
        global _CurrentRenderer
        _window = _PygameClsSdlWindow(title, size, fullscreen=full_screen, resizable=resizable)
        window = Window(_window)
        _WindowsMap[_window] = window
        _Windows.add(window)
        _CurrentRenderer = window._renderer
        _window_create.append(window)
        if _window_create_event:
            _window_create_event.set()
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
        _Windows.remove(self)
        _window_destroy.append(self)
        if _window_destroy_event:
            _window_destroy_event.set()
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

# TODO: lock
_running = False

class InvalidLoopStateException(Exception):
    pass

def stop():
    global _running
    if _running:
        _running = False
        _window_create_event.set()
        _window_destroy_event.set()
    else:
        raise InvalidLoopStateException()

_cleanups = list()

def uninit():
    if _running:
        raise InvalidLoopStateException()
    pygame.quit()

def _default_close(window: Window):
    window.destroy()
    if not _Windows:
        stop()

_CurrentRenderer = None

def _current_renderer():
    return _CurrentRenderer

_PreRenderHooks = set()

async def _draw_async(window: Window):
    global _CurrentRenderer
    while _running:
        if window not in _Windows:
            break
        renderer = window.renderer
        renderer.target = None
        renderer.clear()
        _CurrentRenderer = renderer
        for c in _PreRenderHooks:
            c()
        if await window.dispatch_async('on_draw_async'):
            renderer.update()
        await asyncio.sleep(0)

class InvalidRendererStateException(Exception):
    pass

def current_renderer() -> Renderer:
    if _CurrentRenderer:
        return _CurrentRenderer
    else:
        raise InvalidRendererStateException()

_DEFAULT_EVENTHANDLERS = dict(
    on_close=_default_close,
)

def dispatch_event(window, event, *args, **kwargs):
    if event in window.handlers:
        return window.dispatch(event, *args, **kwargs)
    else:
        try:
            func = _DEFAULT_EVENTHANDLERS[event]
        except KeyError:
            return

        return func(window, *args, **kwargs)

_mouses = _mouse.NButton

async def _run_event():
    global _running
    global _mouses

    pygame.event.clear()
    _mouses = _mouse._mouse_from_pygtpl(pygame.mouse.get_pressed(5))

    while _running:
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if not _running:
                return

            _window = getattr(event, 'window', None)
            if _window:
                window = Window.get(_window)
                _CurrentRenderer = window.renderer
            else:
                window = None

            # TODO: LoOkUp FuNcTiOnS!?!
            if event.type == pygame.QUIT:
                _running = False
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
                dispatch_event(window, 'on_key_press', key, mod)
            elif event.type == pygame.KEYUP:
                try:
                    key = Keys(event.key)
                except ValueError:
                    key = event.key
                try:
                    mod = Keys(event.mod)
                except ValueError:
                    mod = event.mod
                dispatch_event(window, 'on_key_release', key, mod)
            elif event.type == pygame.MOUSEMOTION:
                _mouses = _mouse._mouse_from_pygtpl(event.buttons)
                if _mouses != _mouse.NButton:
                    dispatch_event(window, 'on_mouse_drag', *event.pos, *event.rel, _mouses)
                else:
                    dispatch_event(window, 'on_mouse_motion', *event.pos, *event.rel)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == pygame.BUTTON_WHEELDOWN or event.button == pygame.BUTTON_WHEELUP:
                    continue
                button = _mouse._mouse_from_pyg(event.button)
                _mouses &= ~button
                last = False
                if _mouses == _mouse.NButton:
                    sdl_capturemouse(False)
                    last = True
                dispatch_event(window, 'on_mouse_release', *event.pos, button, pygame.key.get_mods(), last=last)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_WHEELDOWN or event.button == pygame.BUTTON_WHEELUP:
                    continue
                button = _mouse._mouse_from_pyg(event.button)
                first = False
                if _mouses == _mouse.NButton:
                    sdl_capturemouse(True)
                    first = True
                _mouses |= button
                dispatch_event(window, 'on_mouse_press', *event.pos, button, pygame.key.get_mods(), first=first)
            elif event.type == pygame.MOUSEWHEEL:
                if event.flipped:
                    dx = -event.x
                    dy = -event.y
                else:
                    dx = event.x
                    dy = event.y

                dispatch_event(window, 'on_mouse_scroll', *pygame.mouse.get_pos(), dx, dy)
            elif event.type == pygame.WINDOWEVENT:
                if event.event == pygame.WINDOWEVENT_CLOSE:
                    dispatch_event(window, 'on_close')
                elif event.event == pygame.WINDOWEVENT_ENTER:
                    dispatch_event(window, 'on_mouse_enter')
                elif event.event == pygame.WINDOWEVENT_LEAVE:
                    dispatch_event(window, 'on_mouse_leave')
                elif event.event == pygame.WINDOWEVENT_HIDDEN:
                    dispatch_event(window, 'on_hide')
                elif event.event == pygame.WINDOWEVENT_MOVED:
                    dispatch_event(window, 'on_move', -1, -1)
                elif event.event == pygame.WINDOWEVENT_RESIZED:
                    dispatch_event(window, 'on_resize', -1, -1)
                elif event.event == pygame.WINDOWEVENT_SHOWN:
                    dispatch_event(window, 'on_show', -1, -1)

_tasks_dict = dict()

async def _run_window_create():
    global _window_create
    global _window_create_event
    _window_create_event = asyncio.Event()
    while _running:
        for window in _window_create:
            _tasks_dict[window] = asyncio.create_task(_draw_async(window))
        _window_create = list()
        _window_create_event.clear()
        await _window_create_event.wait()

async def _run_window_destroy():
    global _window_destroy
    global _window_destroy_event
    global _tasks_dict
    _window_destroy_event = asyncio.Event()
    while _running:
        for window in _window_destroy:
            await _tasks_dict[window]
            del _tasks_dict[window]
        _window_destroy = list()
        _window_destroy_event.clear()
        await _window_destroy_event.wait()
    for window, task in _tasks_dict.items():
        await task
        if window not in _window_destroy:
            _window_create.append(window)
    _tasks_dict = dict()
    _window_destroy = list()

async def _run_all():
    await asyncio.gather(_run_event(), _run_window_create(), _run_window_destroy())

def run():
    global _running
    if _running:
        raise InvalidLoopStateException()
    _running = True
    asyncio.run(_run_all())
