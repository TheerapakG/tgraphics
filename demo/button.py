import tgraphics

tgraphics.init_with_backend('pygame')

window = tgraphics.Window.create()
grid = tgraphics.Grid(window.size)
grid.add_child_top(tgraphics.shapes.Rectangle(window.size, (255, 255, 255, 255)), (0, 0))

y = 0
def add_element(element):
    global y
    grid.add_child_top(element, (0, y))
    y += element.size[1] + 32


normal_label = tgraphics.text.Label("normal button", 64, color=(0, 0, 0, 255))
normal_label_size = normal_label.size

add_element(tgraphics.Button((normal_label_size[0]+64, normal_label_size[1]+64), fg=normal_label))

toggle_label = tgraphics.text.Label("toggle button", 64, color=(0, 0, 0, 255))
toggle_label_size = toggle_label.size

add_element(tgraphics.Button((toggle_label_size[0]+64, toggle_label_size[1]+64), fg=toggle_label, button_type=tgraphics.ButtonType.TOGGLE))

disable_label = tgraphics.text.Label("disabled button", 64, color=(0, 0, 0, 255))
disable_label_size = disable_label.size

add_element(tgraphics.Button((disable_label_size[0]+64, disable_label_size[1]+64), fg=disable_label, button_type=tgraphics.ButtonType.DISABLE))

window.target_element = grid

tgraphics.run()

tgraphics.uninit()
