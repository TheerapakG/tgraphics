from enum import IntEnum
from pygame import locals

_keys = dict()

for k in dir(locals):
    v = getattr(locals, k)
    if k.startswith('K_'):
        k = k[2:]
    elif k.startswith('KMOD_'):
        k = k[1:]
    else:
        continue

    k.replace('KP', 'NUM')

    if k.isnumeric():
        k = f'_{k}'

    k = k.upper()
    k.replace('EQUALS', 'EQUAL')

    if k == 'EXCLAIM':
        _keys['EXCLAIMATION'] = v
    elif k == 'QUOTEDBL':
        _keys['DOUBLEQUOTE'] = v
    elif k == 'QUOTE':
        _keys[k] = v
        _keys['APOSTROPHE'] = v
    elif k == 'BACKQUOTE':
        _keys[k] = v
        _keys['GRAVE'] = v
    elif k == 'LSUPER':
        _keys[k] = v
        _keys['LWINDOWS'] = v
    elif k == 'RSUPER':
        _keys[k] = v
        _keys['RWINDOWS'] = v
    elif k == 'MOD_NUM':
        _keys['MOD_NUMLOCK'] = v
    elif k == 'MOD_CAPS':
        _keys['MOD_CAPSLOCK'] = v
    else:
        _keys[k] = v

globals().update(_keys)

Keys = IntEnum('Keys', _keys)
