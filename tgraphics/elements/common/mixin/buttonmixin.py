from ..button import Button

class ButtonMixin(Button):
    def __init__(self, *args, bg=None, **kwargs):
        """
        A mixin for transforming an element into a button
        """
        # dict comp is probably faster than iterating once
        # still not sure why one would want to pass in keyword args for button other than bg but it is supported
        _else_kwargs = {key:val for key, val in kwargs.items() if key not in Button.cls_kwargs}
        _btn_kwargs = {key:val for key, val in kwargs.items() if key in Button.cls_kwargs}
        super(Button, self).__init__(*args, **_else_kwargs)
        super().__init__(super(Button, self).size, fg=super(Button, self), bg=bg, **_btn_kwargs)
