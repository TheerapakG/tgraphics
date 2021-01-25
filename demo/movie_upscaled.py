import os
from pathlib import Path

import tgraphics

tgraphics.init_with_backend('pygame')
tgraphics.media.init_with_backend('pyglet')

window = tgraphics.Window.create()
player = tgraphics.media.Player()

os.chdir(Path(__file__).parent)
player.append(tgraphics.media.Source.from_file('bad_apple_480p.mp4'))

window.fps = 60

player.play()
player_size = player.size
window.size = (player_size[0]*1.5, player_size[1]*1.5)
window.target_element = tgraphics.filters.Scale(player, size=window.size)
tgraphics.run()

tgraphics.uninit()
