import os
from pathlib import Path
import sys

# Windows shit
if sys.platform.startswith('win'):
    import ctypes
    _fpath = None
    for _path in os.environ['Path'].split(os.pathsep):
        path = Path(_path)
        if (path/'ffmpeg.exe').exists():
            _fpath = path
            break
        elif (path/'bin'/'ffmpeg.exe').exists():
            _fpath = path/'bin'
            break
    if _fpath:
        ctypes.windll.kernel32.SetDllDirectoryW(str(_fpath))

import tgraphics

tgraphics.init_with_backend('pygame')
tgraphics.media.init_with_backend('pyglet')

window = tgraphics.Window.create()
player = tgraphics.media.Player()

os.chdir(Path(__file__).parent)
player.append(tgraphics.media.Source.from_file('bad_apple.mp4'))

window.target_element = player
window.fps = 60

player.play()
tgraphics.run()

tgraphics.uninit()
