import os
from pathlib import Path

import tgraphics

tgraphics.init_with_backend('pygame')
tgraphics.media.init_with_backend('pyglet')

window = tgraphics.Window.create()
player = tgraphics.media.Player()

os.chdir(Path(__file__).parent)
player.append(tgraphics.media.Source.from_file('bad_apple_{}p.mp4'.format(input("resolution: "))))

window.fps = 60

player.play()
player_size = player.size
print(player_size)
window.size = player_size
window.target_element = tgraphics.filters.Scale(player, size=window.size)
tgraphics.run()

tgraphics.uninit()
