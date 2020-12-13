import tgraphics

tgraphics.init_with_backend('pygame')

window = tgraphics.Window.create()
label = tgraphics.text.Label("hello world!", 100, color=(0, 0, 0, 255))
grid = tgraphics.Grid(window.size)
grid.add_child_top(tgraphics.shapes.Rectangle(window.size, (255, 255, 255, 255)), (0, 0))
grid.add_child_top(label, (0, 0))

window.target_element = grid

tgraphics.run()

tgraphics.uninit()
