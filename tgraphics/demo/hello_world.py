import tgraphics
import pygame.sysfont

tgraphics.init_with_backend('pygame')

window = tgraphics.Window.create()
label = tgraphics.text.Label(u"สวัสดี", "Leelawadee UI", False, False, 100)

window.target_element = label

tgraphics.run()

tgraphics.uninit()
