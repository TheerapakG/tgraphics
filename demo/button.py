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


class DragableButton(tgraphics.mixin.DragableMixin, tgraphics.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


normal_label = tgraphics.text.Label("normal button", 64, color=(0, 0, 0, 255))
normal_label_size = normal_label.size
normal_button = tgraphics.Button((normal_label_size[0]+64, normal_label_size[1]+64), fg=normal_label)
normal_button.event('on_button_press')(lambda: print('normal button pressed'))

add_element(normal_button)

toggle_label = tgraphics.text.Label("toggle button", 64, color=(0, 0, 0, 255))
toggle_label_size = toggle_label.size
toggle_button = tgraphics.Button((toggle_label_size[0]+64, toggle_label_size[1]+64), fg=toggle_label, button_type=tgraphics.ButtonType.TOGGLE)
toggle_button.event('on_button_on')(lambda: print('button toggled on'))
toggle_button.event('on_button_off')(lambda: print('button toggled off'))

add_element(toggle_button)

disable_label = tgraphics.text.Label("disabled button", 64, color=(0, 0, 0, 255))
disable_label_size = disable_label.size
disable_button = tgraphics.Button((disable_label_size[0]+64, disable_label_size[1]+64), fg=disable_label, button_type=tgraphics.ButtonType.DISABLE)
disable_button.event('on_button_press')(lambda: print('disable button pressed'))

add_element(disable_button)

dragable_label = tgraphics.text.Label("dragable button", 64, color=(0, 0, 0, 255))
dragable_label_size = dragable_label.size
dragable_button = DragableButton((dragable_label_size[0]+64, dragable_label_size[1]+64), fg=dragable_label)

add_element(dragable_button)

window.target_element = grid

tgraphics.run()

tgraphics.uninit()
