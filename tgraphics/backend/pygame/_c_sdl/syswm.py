# This software is distributed under the distributed under the Public Domain
# 2012-2020 Marcus von Appen <marcus@sysfault.org>
# 2021 TheerapakG

from ctypes import *

Sint8 = c_int8
Uint8 = c_uint8
Sint16 = c_int16
Uint16 = c_uint16
Sint32 = c_int32
Uint32 = c_uint32
Sint64 = c_int64
Uint64 = c_uint64

HWND = c_void_p
HDC = c_void_p
HINSTANCE = c_void_p
UINT = c_uint
if sizeof(c_long) == sizeof(c_void_p):
    WPARAM = c_ulong
    LPARAM = c_long
elif sizeof(c_longlong) == sizeof(c_void_p):
    WPARAM = c_ulonglong
    LPARAM = c_longlong

class SDL_version(Structure):
    _fields_ = [("major", Uint8),
                ("minor", Uint8),
                ("patch", Uint8),
                ]

SDL_SYSWM_TYPE = c_int

SDL_SYSWM_UNKNOWN = 0
SDL_SYSWM_WINDOWS = 1
SDL_SYSWM_X11 = 2
SDL_SYSWM_DIRECTFB = 3
SDL_SYSWM_COCOA = 4
SDL_SYSWM_UIKIT = 5
SDL_SYSWM_WAYLAND = 6
SDL_SYSWM_MIR = 7
SDL_SYSWM_WINRT = 8
SDL_SYSWM_ANDROID = 9
SDL_SYSWM_VIVANTE = 10
SDL_SYSWM_OS2 = 11
SDL_SYSWM_HAIKU = 12

class _wininfo(Structure):
    _fields_ = [("window", HWND),
                ("hdc", HDC),
                ("hinstance", HINSTANCE)
               ]

class _winrtinfo(Structure):
    _fields_ = [("window", c_void_p)]


class _x11info(Structure):
    """Window information for X11."""
    _fields_ = [("display", c_void_p),
                ("window", c_ulong)]


class _dfbinfo(Structure):
    """Window information for DirectFB."""
    _fields_ = [("dfb", c_void_p),
                ("window", c_void_p),
                ("surface", c_void_p)]


class _cocoainfo(Structure):
    """Window information for MacOS X."""
    _fields_ = [("window", c_void_p)]


class _uikitinfo(Structure):
    """Window information for iOS."""
    _fields_ = [("window", c_void_p),
                ("framebuffer", Uint32),
                ("colorbuffer", Uint32),
                ("resolveFramebuffer", Uint32)]


class _wl(Structure):
    """Window information for Wayland."""
    _fields_ = [("display", c_void_p),
                ("surface", c_void_p),
                ("shell_surface", c_void_p)]

class _mir(Structure):
    """Window information for Mir."""
    _fields_ = [("connection", c_void_p),
                ("surface", c_void_p)]


class _android(Structure):
    """Window information for Android."""
    _fields_ = [("window", c_void_p),
                ("surface", c_void_p)]


class _vivante(Structure):
    """Window information for Vivante."""
    _fields_ = [("display", c_void_p),
                ("window", c_void_p)]

class _info(Union):
    """The platform-specific information of a window."""
    _fields_ = [("win", _wininfo),
                ("winrt", _winrtinfo),
                ("x11", _x11info),
                ("dfb", _dfbinfo),
                ("cocoa", _cocoainfo),
                ("uikit", _uikitinfo),
                ("wl", _wl),
                ("mir", _mir),
                ("android", _android),
                ("vivante", _vivante),
                ("dummy", (Uint8 * 64))
               ]


class SDL_SysWMinfo(Structure):
    """System-specific window manager information.
    This holds the low-level information about the window.
    """
    _fields_ = [("version", SDL_version),
                ("subsystem", SDL_SYSWM_TYPE),
                ("info", _info)
               ]
