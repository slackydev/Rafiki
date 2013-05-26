import os,sys
abspath = os.path.abspath(__file__)
srcpath = os.path.dirname(abspath)+os.sep+'..'+os.sep+'..'
sys.path.insert(1, srcpath)

from pywin_api.conn import *
from pywin_api import winapi
from time import sleep

from .stub import MouseMeta

BASE = ['mbleft', 'mbmdl', 'mbright']

BUTTON_DOWN = { 
  1: (MOUSE_LEFTDOWN, 0),
  2: (MOUSE_MIDDLEDOWN, 0),
  3: (MOUSE_RIGHTDOWN, 0),
  4: (MOUSE_WHEEL, 0), #EMPTY
  5: (MOUSE_WHEEL, 0), #EMPTY
  6: (MOUSE_HWHEEL, 0), #EMPTY
  7: (MOUSE_HWHEEL, 0)  #EMPTY
}
BUTTON_UP = { 
  1: (MOUSE_LEFTUP, 0),
  2: (MOUSE_MIDDLEUP, 0), 
  3: (MOUSE_RIGHTUP, 0),
  4: (MOUSE_WHEEL,  1), #UP
  5: (MOUSE_WHEEL, -1), #DOWN
  6: (MOUSE_HWHEEL,-1), #LEFT
  7: (MOUSE_HWHEEL, 1)  #RIGHT
}

BUTTON = {
  'mbleft':  1,
  'mbmdl':   2,
  'mbright': 3,
  'scroll_up':    4, 
  'scroll_down':  5, 
  'scroll_left':  6, 
  'scroll_right': 7
}

class Mouse(MouseMeta):
    def press(self, x, y, button=1):
        if isinstance(button, str): 
            button = BUTTON.get(button)
        action, e = BUTTON_DOWN.get(button)
            
        self.move(x,y)
        winapi.mouse_event(action, x, y, e, 0)
        print action
        
    def release(self, x, y, button=1):
        if isinstance(button, str): 
            button = BUTTON.get(button)
        action, e = BUTTON_UP.get(button)
            
        self.move(x,y)
        winapi.mouse_event(action, x, y, 0,0)
        print action

    def btn_state(self, button=1):
        if button == 1: return winapi.GetAsyncKeyState(0x01) > 0
        if button == 2: return winapi.GetAsyncKeyState(0x04) > 0
        if button == 3: return winapi.GetAsyncKeyState(0x02) > 0
        return False

    def move(self, x, y):
        winapi.SetCursorPos(x, y)

    def position(self):
        return winapi.GetCursorPos()