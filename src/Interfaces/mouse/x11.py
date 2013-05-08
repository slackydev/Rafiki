from Xlib.display import Display
from Xlib import X
from Xlib.ext.xtest import fake_input

from .base import MouseMeta

BUTTONS = { 
    'mbleft':       1, 
    'mbmdl':        2, 
    'mbright':      3, 
    'scroll_up':    4, 
    'scroll_down':  5,
    'scroll_left':  6,
    'scroll_right': 7,
}


class Mouse(MouseMeta):
    def __init__(self, display=None):
        MouseMeta.__init__(self)
        self.display = Display(display)

    def press(self, x, y, button = 1):
        if isinstance(button, str): 
            button = BUTTONS.get(button)
            if not button: return 
        self.move(x, y)
        fake_input(self.display, X.ButtonPress, button)
        self.display.sync()

    def release(self, x, y, button = 1):
        if isinstance(button, str): 
            button = BUTTONS.get(button)
            if not button: return 
        self.move(x, y)
        fake_input(self.display, X.ButtonRelease, button)
        self.display.sync()

    def move(self, x, y):
        #--self.display.screen().root.warp_pointer(x,y)
        fake_input(self.display, X.MotionNotify, x=x, y=y)
        self.display.sync()

    def position(self):
        coord = self.display.screen().root.query_pointer()._data
        return coord["root_x"], coord["root_y"]






