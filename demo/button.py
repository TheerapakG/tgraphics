import tgraphics

tgraphics.init_with_backend('pygame')

window = tgraphics.Window.create()
grid = tgraphics.Grid(window.size)
grid.add_child_top(tgraphics.shapes.Rectangle(window.size, (255, 255, 255, 255)), (0, 0))

y = 0
def add_element(element):
    global y
    grid.add_child_top(element, (0, y))
    y += element.size[1] + 16


class DragableButton(tgraphics.mixin.DragableMixin, tgraphics.LabelButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DropSensor(tgraphics.Grid):
    def __init__(self, text):
        label = tgraphics.text.Label(text, 64, color=(255, 255, 255, 255))
        label_size = label.size
        sz = (label_size[0]+64, label_size[1]+64)
        super().__init__(sz)
        self.add_child_top(tgraphics.shapes.Rectangle(sz, color=(128, 128, 128, 255)), (0, 0))
        self.add_child_top(label, (32, 32))
        self._dark_rect = tgraphics.shapes.Rectangle(sz, color=(0, 0, 0, 255))

        @self.event
        def on_element_dropped(x, y, element):
            self.dark(False)
            print(element, 'dropped inside sensor at ({x}, {y})'.format(x=x, y=y))
            return True

        @self.event
        def on_element_enter(element):
            self.dark(True)
            return True

        @self.event
        def on_element_leave(element):
            self.dark(False)
            return True

    def dark(self, dark):
        if dark:
            self.add_child(1, self._dark_rect, (0, 0))
        else:
            try:
                self.remove_child(self._dark_rect)
            except ValueError:
                pass


add_element(DropSensor('maybe try dropping element here'))

normal_button = tgraphics.LabelButton.with_margin("normal button", 64, 64, color=(0, 0, 0, 255))
normal_button.event('on_button_press')(lambda: print('normal button pressed'))

add_element(normal_button)

toggle_button = tgraphics.LabelButton.with_margin("toggle button", 64, 64, color=(0, 0, 0, 255), button_type=tgraphics.ButtonType.TOGGLE)
toggle_button.event('on_button_on')(lambda: print('button toggled on'))
toggle_button.event('on_button_off')(lambda: print('button toggled off'))

add_element(toggle_button)

disable_button = tgraphics.LabelButton.with_margin("disabled button", 64, 64, color=(0, 0, 0, 255), button_type=tgraphics.ButtonType.DISABLE)
disable_button.event('on_button_press')(lambda: print('disabled button pressed'))

add_element(disable_button)

dragable_button = DragableButton.with_margin("dragable button", 64, 64, color=(0, 0, 0, 255))

add_element(dragable_button)

window.target_element = grid
window.fps = 60

tgraphics.run()

tgraphics.uninit()
