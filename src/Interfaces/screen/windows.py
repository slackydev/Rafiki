from ..pywin_api.con import *
from ..pywin_api import winapi


def getWindowFromMouse():
    x,y = winapi.GetCursorPos()
    hwnd = winapi.WindowFromPoint((x,y))
