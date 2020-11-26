from pygame import key as _key

_keys = dict()

for k in dir(_key):
    v = getattr(_key, k)
    if k.startswith('K_'):
        k = k[2:]
    elif k.startswith('KMOD_'):
        k = k[1:]

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
