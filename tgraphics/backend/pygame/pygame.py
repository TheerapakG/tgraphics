from collections import defaultdict
from enum import Enum
from functools import partial
import os

os.environ['PYGAME_FREETYPE'] = "1"
import pygame

from . import mouse

# pylint: disable=no-member
import pygame._sdl2

_PygameFlagSdl_WINDOWPOS_UNDEFINED = getattr(pygame, "WINDOWPOS_UNDEFINED", pygame._sdl2.WINDOWPOS_UNDEFINED)
_PygameClsSdlWindow = getattr(pygame, "Window", pygame._sdl2.Window)
_PygameClsSdlRenderer = getattr(pygame, "Renderer", pygame._sdl2.Renderer)
_PygameClsSdlTexture= getattr(pygame, "Renderer", pygame._sdl2.Texture)

class Renderer:
    def __init__(self, _pyg):
        self._window, self._renderer = _pyg
        self.draw_color = (0, 0, 0, 255)

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
                return self._renderer.target

            def __call__(self, new_target):
                class _TargetCtxMgrProxy:
                    def __init__(self, renderer):
                        self._renderer = renderer
                        self._replacing = []

                    def __enter__(self):
                        self._replacing.append(self._renderer.target)
                        self._renderer.target = new_target

                    def __exit__(self, type, value, traceback):
                        self._renderer.target = self._replacing.pop()
                
                return _TargetCtxMgrProxy(self._renderer)

        return _TargetGetProxy(self._renderer)

    @target.setter
    def target(self, new_target):
        self._renderer.target = new_target

    @property
    def draw_color(self):
        class _ColorGetProxy:
            def __init__(self, renderer):
                self._renderer = renderer

            def get(self):
                return self._renderer.draw_color

            def __call__(self, new_color):
                class _ColorCtxMgrProxy:
                    def __init__(self, renderer):
                        self._renderer = renderer
                        self._replacing = []

                    def __enter__(self):
                        self._replacing.append(self._renderer.draw_color)
                        self._renderer.draw_color = new_color

                    def __exit__(self, type, value, traceback):
                        self._renderer.draw_color = self._replacing.pop()
                
                return _ColorCtxMgrProxy(self._renderer)

        return _ColorGetProxy(self._renderer)

    @draw_color.setter
    def draw_color(self, new_color):
        self._renderer.draw_color = new_color

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

_WindowsMap = dict()
_Windows = set()

class Window:
    def __init__(self, _pyg):
        self._window = _pyg
        if _pyg in _WindowsMap:
            other = _WindowsMap[_pyg]
            self._renderer = other._renderer
            self._funcs = other._funcs
        else:
            try:
                self._renderer = Renderer((self, _PygameClsSdlRenderer.from_window(self._window)))
            except pygame._sdl2.sdl2.error:
                self._renderer = Renderer((self, _PygameClsSdlRenderer(self._window, target_texture=True)))
            self._funcs = defaultdict(lambda: None)

    @staticmethod
    def create(title, size, full_screen, resizable):
        _window = _PygameClsSdlWindow(title, size, fullscreen=full_screen, resizable=resizable)
        window = Window(_window)
        _WindowsMap[_window] = window
        _Windows.add(window)
        return window

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

    def icon(self, surface):
        self._window.set_icon(surface)

    icon = property(None, icon)

    @property
    def id(self):
        return self._window.id

    @property
    def renderer(self):
        return self._renderer

    def event(self, func, *, name=None):
        if isinstance(func, str):
            return partial(self.event, name=func)
        self._funcs[name if name else func.__name__] = func

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


# reimplementation of SDL_TextureAccess enum as pygame does not expose it
class TextureAccessEnum(Enum):
    Static = 0
    Streaming = 1
    Target = 2


class Texture:
    def __init__(self, _pyg=None):
        self._renderer, self._texture = _pyg

    @staticmethod
    def create(renderer: Renderer, size, access: TextureAccessEnum=TextureAccessEnum.Static):
        if access == TextureAccessEnum.Static:
            _n_dict = {'static': True}
        elif access == TextureAccessEnum.Streaming:
            _n_dict = {'streaming': True}
        elif access == TextureAccessEnum.Static:
            _n_dict = {'target': True}
        return Texture((renderer, _PygameClsSdlTexture(renderer._renderer, size, **_n_dict)))

    @staticmethod
    def from_surface(renderer: Renderer, surface: Surface):
        return Texture((renderer, _PygameClsSdlTexture.from_surface(renderer._renderer, surface._surface)))

    @staticmethod
    def from_file(renderer: Renderer, filename):
        return Texture.from_surface(renderer, Surface.from_file(filename))

    @staticmethod
    def from_io(renderer: Renderer, io, ext_hint):
        return Texture.from_surface(renderer, Surface.from_io(io, ext_hint))

    @property
    def w(self):
        return self._texture.width

    @property
    def h(self):
        return self._texture.height

    @property
    def size(self):
        return self.w, self.h

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

def _default_draw(window: Window):
    global _CurrentRenderer
    renderer = window.renderer
    renderer.target = None
    renderer.clear()
    if func := window._funcs['on_draw']:
        _CurrentRenderer = renderer
        func()
    renderer.update()

class InvalidRendererStateException(Exception):
    pass

def _current_renderer() -> Renderer:
    if _CurrentRenderer:
        return _CurrentRenderer
    else:
        raise InvalidRendererStateException()

_DEFAULT_EVENTHANDLERS = dict(
    on_close=_default_close,
    _on_draw=_default_draw,
)

def dispatch_event(window, event, *args, **kwargs):
    if func := window._funcs[event]:
        func(*args, **kwargs)
    else:
        try:
            func = _DEFAULT_EVENTHANDLERS[event]
        except KeyError:
            return

        func(window, *args, **kwargs)

def run():
    global _running
    if _running:
        raise InvalidLoopStateException()
    _running = True
    while _running:
        for event in pygame.event.get():
            if _window := getattr(event, 'window', None):
                window = Window(_window)
            if event.type == pygame.QUIT:
                dispatch_event(window, 'on_close')
            elif event.type == pygame.KEYDOWN:
                dispatch_event(window, 'on_key_press', event.key, event.mod)
            elif event.type == pygame.KEYUP:
                dispatch_event(window, 'on_key_release', event.key, event.mod)
            elif event.type == pygame.MOUSEMOTION:
                if any(event.buttons):
                    dispatch_event(window, 'on_mouse_drag', *event.pos, *event.rel, mouse._mouse_from_pygtpl(event.buttons))
                else:
                    dispatch_event(window, 'on_mouse_motion', *event.pos, *event.rel)
            elif event.type == pygame.MOUSEBUTTONUP:
                dispatch_event(window, 'on_mouse_release', *event.pos, mouse._mouse_from_pyg(event.button), pygame.key.set_mods())
            elif event.type == pygame.MOUSEBUTTONDOWN:
                dispatch_event(window, 'on_mouse_press', *event.pos, mouse._mouse_from_pyg(event.button), pygame.key.set_mods())
            elif event.type == pygame.MOUSEWHEEL:
                if event.flipped:
                    dx = -event.x
                    dy = -event.y
                else:
                    dx = event.x
                    dy = event.y

                dispatch_event(window, 'on_mouse_scroll', *pygame.mouse.get_pos(), dx, dy)
                
        for window in _Windows:
            dispatch_event(window, '_on_draw')
