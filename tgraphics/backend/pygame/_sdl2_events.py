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

SDL_FIRSTEVENT = 0
SDL_QUIT = 0x100
SDL_APP_TERMINATING = 0x101
SDL_APP_LOWMEMORY = 0x102
SDL_APP_WILLENTERBACKGROUND = 0x103
SDL_APP_DIDENTERBACKGROUND = 0x104
SDL_APP_WILLENTERFOREGROUND = 0x105
SDL_APP_DIDENTERFOREGROUND = 0x106
SDL_DISPLAYEVENT = 0x150
SDL_WINDOWEVENT = 0x200
SDL_SYSWMEVENT = 0x201
SDL_KEYDOWN = 0x300
SDL_KEYUP = 0x301
SDL_TEXTEDITING = 0x302
SDL_TEXTINPUT = 0x303
SDL_KEYMAPCHANGED = 0x304
SDL_MOUSEMOTION = 0x400
SDL_MOUSEBUTTONDOWN = 0x401
SDL_MOUSEBUTTONUP = 0x402
SDL_MOUSEWHEEL = 0x403
SDL_JOYAXISMOTION = 0x600
SDL_JOYBALLMOTION = 0x601
SDL_JOYHATMOTION = 0x602
SDL_JOYBUTTONDOWN = 0x603
SDL_JOYBUTTONUP = 0x604
SDL_JOYDEVICEADDED = 0x605
SDL_JOYDEVICEREMOVED = 0x606
SDL_CONTROLLERAXISMOTION = 0x650
SDL_CONTROLLERBUTTONDOWN = 0x651
SDL_CONTROLLERBUTTONUP = 0x652
SDL_CONTROLLERDEVICEADDED = 0x653
SDL_CONTROLLERDEVICEREMOVED = 0x654
SDL_CONTROLLERDEVICEREMAPPED = 0x655
SDL_FINGERDOWN = 0x700
SDL_FINGERUP = 0x701
SDL_FINGERMOTION = 0x702
SDL_DOLLARGESTURE = 0x800
SDL_DOLLARRECORD = 0x801
SDL_MULTIGESTURE = 0x802
SDL_CLIPBOARDUPDATE = 0x900
SDL_DROPFILE = 0x1000
SDL_DROPTEXT = 0x1001
SDL_DROPBEGIN = 0x1002
SDL_DROPCOMPLETE = 0x1003
SDL_AUDIODEVICEADDED = 0x1100
SDL_AUDIODEVICEREMOVED = 0x1101
SDL_SENSORUPDATE = 0x1200
SDL_RENDER_TARGETS_RESET = 0x2000
SDL_RENDER_DEVICE_RESET = 0x2001
SDL_USEREVENT = 0x8000
SDL_LASTEVENT = 0xFFFF
SDL_EventType = c_int

SDL_RELEASED = 0
SDL_PRESSED = 1


class SDL_CommonEvent(Structure):
    _fields_ = [("type", Uint32), ("timestamp", Uint32)]

class SDL_DisplayEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("display", Uint32),
                ("event", Uint8),
                ("padding1", Uint8),
                ("padding2", Uint8),
                ("padding3", Uint8),
                ("data1", Sint32)
                ]

class SDL_WindowEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("windowID", Uint32),
                ("event", Uint8),
                ("padding1", Uint8),
                ("padding2", Uint8),
                ("padding3", Uint8),
                ("data1", Sint32),
                ("data2", Sint32)
                ]

SDL_Scancode = c_int
SDL_Keycode = Sint32

class SDL_Keysym(Structure):
    _fields_ = [("scancode", SDL_Scancode),
                ("sym", SDL_Keycode),
                ("mod", Uint16),
                ("unused", Uint32)
                ]

class SDL_KeyboardEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("windowID", Uint32),
                ("state", Uint8),
                ("repeat", Uint8),
                ("padding2", Uint8),
                ("padding3", Uint8),
                ("keysym", SDL_Keysym)
                ]

SDL_TEXTEDITINGEVENT_TEXT_SIZE = 32

class SDL_TextEditingEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("windowID", Uint32),
                ("text", (c_char * SDL_TEXTEDITINGEVENT_TEXT_SIZE)),
                ("start", Sint32),
                ("length", Sint32)
                ]

SDL_TEXTINPUTEVENT_TEXT_SIZE = 32
class SDL_TextInputEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("windowID", Uint32),
                ("text", (c_char * SDL_TEXTINPUTEVENT_TEXT_SIZE))
                ]

class SDL_MouseMotionEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("windowID", Uint32),
                ("which", Uint32),
                ("state", Uint32),
                ("x", Sint32),
                ("y", Sint32),
                ("xrel", Sint32),
                ("yrel", Sint32)
                ]

class SDL_MouseButtonEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("windowID", Uint32),
                ("which", Uint32),
                ("button", Uint8),
                ("state", Uint8),
                ("clicks", Uint8),
                ("padding1", Uint8),
                ("x", Sint32),
                ("y", Sint32)
                ]

class SDL_MouseWheelEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("windowID", Uint32),
                ("which", Uint32),
                ("x", Sint32),
                ("y", Sint32),
                ("direction", Uint32)
                ]

SDL_JoystickID = Sint32

class SDL_JoyAxisEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", SDL_JoystickID),
                ("axis", Uint8),
                ("padding1", Uint8),
                ("padding2", Uint8),
                ("padding3", Uint8),
                ("value", Sint16),
                ("padding4", Uint16)
                ]

class SDL_JoyBallEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", SDL_JoystickID),
                ("ball", Uint8),
                ("padding1", Uint8),
                ("padding2", Uint8),
                ("padding3", Uint8),
                ("xrel", Sint16),
                ("yrel", Sint16)
                ]

class SDL_JoyHatEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", SDL_JoystickID),
                ("hat", Uint8),
                ("value", Uint8),
                ("padding1", Uint8),
                ("padding2", Uint8)
                ]

class SDL_JoyButtonEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", SDL_JoystickID),
                ("button", Uint8),
                ("state", Uint8),
                ("padding1", Uint8),
                ("padding2", Uint8)
                ]

class SDL_JoyDeviceEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", Sint32)
                ]

class SDL_ControllerAxisEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", SDL_JoystickID),
                ("axis", Uint8),
                ("padding1", Uint8),
                ("padding2", Uint8),
                ("padding3", Uint8),
                ("value", Sint16),
                ("padding4", Uint16)
                ]

class SDL_ControllerButtonEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", SDL_JoystickID),
                ("button", Uint8),
                ("state", Uint8),
                ("padding1", Uint8),
                ("padding2", Uint8)
                ]

class SDL_ControllerDeviceEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", Sint32)
                ]

class SDL_AudioDeviceEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", Uint32),
                ("iscapture", Uint8),
                ("padding1", Uint8),
                ("padding2", Uint8),
                ("padding3", Uint8)
            ]

SDL_TouchID = Sint64
SDL_FingerID = Sint64

class SDL_TouchFingerEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("touchId", SDL_TouchID),
                ("fingerId", SDL_FingerID),
                ("x", c_float),
                ("y", c_float),
                ("dx", c_float),
                ("dy", c_float),
                ("pressure", c_float),
                ("windowID", Uint32)
                ]

class SDL_MultiGestureEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("touchId", SDL_TouchID),
                ("dTheta", c_float),
                ("dDist", c_float),
                ("x", c_float),
                ("y", c_float),
                ("numFingers", Uint16),
                ("padding", Uint16)
                ]

SDL_GestureID = Sint64

class SDL_DollarGestureEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("touchId", SDL_TouchID),
                ("gestureId", SDL_GestureID),
                ("numFingers", Uint32),
                ("error", c_float),
                ("x", c_float),
                ("y", c_float)
                ]

class SDL_DropEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("file", c_char_p),
                ("windowID", Uint32)
                ]

class SDL_SensorEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("which", Sint32),
                ("data", (c_float * 6))
                ]

class SDL_QuitEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32)
                ]

class SDL_OSEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32)
                ]

class SDL_UserEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("windowID", Uint32),
                ("code", Sint32),
                ("data1", c_void_p),
                ("data2", c_void_p)
                ]

class _winmsg(Structure):
    _fields_ = [("hwnd", HWND),
                ("msg", UINT),
                ("wParam", WPARAM),
                ("lParam", LPARAM),
               ]

class _x11msg(Structure):
    _fields_ = [("event", c_void_p)]


class _dfbmsg(Structure):
    _fields_ = [("event", c_void_p)]


class _cocoamsg(Structure):
    _fields_ = [("dummy", c_int)]


class _uikitmsg(Structure):
    _fields_ = [("dummy", c_int)]


class _vivantemsg(Structure):
    _fields_ = [("dummy", c_int)]


class _msg(Union):
    _fields_ = [("win", _winmsg),
                ("x11", _x11msg),
                ("dfb", _dfbmsg),
                ("cocoa", _cocoamsg),
                ("uikit", _uikitmsg),
                ("vivante", _vivantemsg),
                ("dummy", c_int)
               ]

class SDL_version(Structure):
    _fields_ = [("major", Uint8),
                ("minor", Uint8),
                ("patch", Uint8),
                ]

SDL_SYSWM_TYPE = c_int

class SDL_SysWMmsg(Structure):
    _fields_ = [("version", SDL_version),
                ("subsystem", SDL_SYSWM_TYPE),
                ("msg", _msg)
               ]

class SDL_SysWMEvent(Structure):
    _fields_ = [("type", Uint32),
                ("timestamp", Uint32),
                ("msg", POINTER(SDL_SysWMmsg))
                ]

class SDL_Event(Union):
    _fields_ = [("type", Uint32),
                ("common", SDL_CommonEvent),
                ("display", SDL_DisplayEvent),
                ("window", SDL_WindowEvent),
                ("key", SDL_KeyboardEvent),
                ("edit", SDL_TextEditingEvent),
                ("text", SDL_TextInputEvent),
                ("motion", SDL_MouseMotionEvent),
                ("button", SDL_MouseButtonEvent),
                ("wheel", SDL_MouseWheelEvent),
                ("jaxis", SDL_JoyAxisEvent),
                ("jball", SDL_JoyBallEvent),
                ("jhat", SDL_JoyHatEvent),
                ("jbutton", SDL_JoyButtonEvent),
                ("jdevice", SDL_JoyDeviceEvent),
                ("caxis", SDL_ControllerAxisEvent),
                ("cbutton", SDL_ControllerButtonEvent),
                ("cdevice", SDL_ControllerDeviceEvent),
                ("adevice", SDL_AudioDeviceEvent),
                ("sensor", SDL_SensorEvent),
                ("quit", SDL_QuitEvent),
                ("user", SDL_UserEvent),
                ("syswm", SDL_SysWMEvent),
                ("tfinger", SDL_TouchFingerEvent),
                ("mgesture", SDL_MultiGestureEvent),
                ("dgesture", SDL_DollarGestureEvent),
                ("drop", SDL_DropEvent),
                ("padding", (Uint8 * 56)),
                ]
                