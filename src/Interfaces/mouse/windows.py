from ..pywin_api.con import *
from ..pywin_api import winapi
from time import sleep

from .base import MouseMeta

BASE = ['mbleft', 'mbmdl', 'mbright']

BUTTON = {
  'mbleft':  (MOUSE_LEFTDOWN,   MOUSE_LEFTUP),
  'mbmdl':   (MOUSE_MIDDLEDOWN, MOUSE_MIDDLEUP),
  'mbright': (MOUSE_RIGHTDOWN,  MOUSE_RIGHTUP)
  'scroll_up':    (MOUSE_WHEEL,  1), 
  'scroll_down':  (MOUSE_WHEEL,  -1), 
  'scroll_left':  (MOUSE_HWHEEL, -1), 
  'scroll_right': (MOUSE_HWHEEL, 1),
}

BUTTON_UP = { 
  1: MOUSE_LEFTDOWN, 
  2: MOUSE_MIDDLEDOWN, 
  3: MOUSE_RIGHTDOWN,
  4: (MOUSE_WHEEL, 0), #EMPTY
  5: (MOUSE_WHEEL, 0), #EMPTY
  6: (MOUSE_HWHEEL,0), #EMPTY
  7: (MOUSE_HWHEEL,0)  #EMPTY
}
BUTTON_DOWN = { 
  1: MOUSE_LEFTUP,  
  2: MOUSE_MIDDLEUP, 
  3: MOUSE_RIGHTUP,
  4: (MOUSE_WHEEL,  1), #UP
  5: (MOUSE_WHEEL, -1), #DOWN
  6: (MOUSE_HWHEEL,-1), #LEFT
  7: (MOUSE_HWHEEL, 1), #RIGHT
}

class Mouse(MouseMeta):
    def press(self, x, y, button):
        if isinstance(button, str): 
          i = 0
          if button in BASE:
            action = BUTTON.get(button)[0]
          else:
            action, i = BUTTON.get(button)


        else: action = BUTTON_DOWN.get(button)                         
        self.move(x,y)
        winapi.mouse_event(action, x, y, i, 0)
        
    def release(self, x, y, button = 1):
        if isinstance(button, str): 
          if button in BASE:
            action = BUTTON.get(button)[1]
          else:
            action, i = BUTTON.get(button)

        else: action = BUTTON_UP.get(button)[1]
        self.move(x,y)
        winapi.mouse_event(action, x, y, 0,0)

    def move(self, x, y):
        winapi.SetCursorPos(x, y)

    def position(self):
        return winapi.GetCursorPos()
        
