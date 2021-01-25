import os
from pathlib import Path

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
