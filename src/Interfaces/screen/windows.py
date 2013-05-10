import os,sys
abspath = os.path.abspath(__file__)
srcpath = os.path.dirname(abspath)+os.sep+'..'+os.sep+'..'
sys.path.insert(1, srcpath)

from pywin_api.conn import *
from pywin_api import winapi


#-----------------------------------------------------------------------
def getScreenSize():
  width = winapi.GetSystemMetrics(SM_CXVIRTUALSCREEN)
  height = winapi.GetSystemMetrics(SM_CYVIRTUALSCREEN)
  return width,height

#-----------------------------------------------------------------------
def getDesktopScreenSize():
  width = winapi.GetSystemMetrics(0)
  height = winapi.GetSystemMetrics(1)
  return width,height

#-----------------------------------------------------------------------
def isRealWindow(hwnd):
    ''' Check if a given window is a real Windows application frame..
        Returns a BOOL
    '''
    if not winapi.IsWindowVisible(hwnd):
        return False
    if win32gui.GetParent(hwnd) != 0:
        return False
    hasNoOwner = winapi.GetWindow(hwnd, GW_OWNER) == 0
    lExStyle = winapi.GetWindowLong(hwnd, GWL_EXSTYLE)
    if (((lExStyle & WS_EX_TOOLWINDOW) == 0 and hasNoOwner)
      or ((lExStyle & WS_EX_APPWINDOW != 0) and not hasNoOwner)):
        if winapi.GetWindowText(hwnd):
            return True
    return False
  
#-----------------------------------------------------------------------
def getWindowByName(framename):
    window = []
    hwnds = winapi.EnumWindows()
    for hwnd in hwnds:
        if not isRealWindow(hwnd):
            return None
        else:
            title = winapi.GetWindowText(hwnd)
            if framename in title:
                return hwnd
    return None

#-----------------------------------------------------------------------
def getVisibleWindows():
    windows = []
    hwnds = winapi.EnumWindows()
    for hwnd in hwnds:
        if not isRealWindow(hwnd):
            return None
        else:
            windows.append(hwnd)
    return windows
    
def getWindowRect(hwin):
    rect = winapi.GetWindowRect(hwnd)
    sx, sy = frame[0], frame[1]
    ex, ey = frame[2], frame[3]
    return sx,sy, ex-sx, ey-sy
    
#-----------------------------------------------------------------------
def getWindowFromPointer():
    point = winapi.GetCursorPos()
    hwnd = winapi.WindowFromPoint(point)
    return hwnd
    
#-----------------------------------------------------------------------
def getWindowFromPoint(point, skipz=[]):
    hwnd = winapi.WindowFromPoint(point)
    return hwnd
    
#-----------------------------------------------------------------------
def get_pixel_colour(i_x, i_y):
  hwnd = winapi.GetDesktopWindow()
  winDC = winapi.GetWindowDC(hwnd)
  color = winapi.GetPixel(winDC, i_x, i_y)
  rgb = (color & 0xff), ((color >> 8) & 0xff), ((color >> 16) & 0xff)
  winapi.ReleaseDC(hwnd, winDC)
  return rgb
  
  