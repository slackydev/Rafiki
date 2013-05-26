'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 This file is part of the Rafiki Macro Library (RML)
 Copyright (c) 2012-2013 by Jarl Holta

 RML is free software: you can redistribute it and/or modify
 it under the terms of the wxWindows licence.

 RML is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

 wxWindows licence: <http://opensource.org/licenses/wxwindows.php>
 You might have recieved a copy of the lisence.

 --- (Windows) Screen control for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
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
def getRoot():
    hwnd = winapi.GetDesktopWindow()
    return hwnd

#-----------------------------------------------------------------------
def isRealWindow(hwnd):
    ''' Check if a given window is a real Windows application frame..
        Returns a BOOL
    '''
    if not winapi.IsWindowVisible(hwnd):
        return False
    if winapi.GetParent(hwnd) != 0:
        return False
    hasNoOwner = winapi.GetWindow(hwnd, GW_OWNER) == 0
    lExStyle = winapi.GetWindowLong(hwnd, GWL_EXSTYLE)
    if (((lExStyle & WS_EX_TOOLWINDOW) == 0 and hasNoOwner)
      or ((lExStyle & WS_EX_APPWINDOW != 0) and not hasNoOwner)):
        if winapi.GetWindowText(hwnd):
            return True
    return False
  
#-----------------------------------------------------------------------
def getWindowByName(title):
    window = []
    hwnds = winapi.EnumWindows()
    for hwnd in hwnds:
        if not isRealWindow(hwnd):
            pass
        else:
            wndtitle = winapi.GetWindowText(hwnd)
            if title.lower() in wndtitle.lower():
                return (hwnd, wndtitle)
    return False

#-----------------------------------------------------------------------
def getVisibleWindows():
    windows = []
    hwnds = winapi.EnumWindows()
    for hwnd in hwnds:
        if not isRealWindow(hwnd):
            pass
        else:
            windows.append(hwnd)
    return windows

#-----------------------------------------------------------------------    
def getWindowRect(winID):
    rect = winapi.GetWindowRect(winID)
    sx, sy = rect[0], rect[1]
    ex, ey = rect[2], rect[3]
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
def getWindowTitle(winID):
    name = winapi.GetWindowText(winID)
    return name

#-----------------------------------------------------------------------
def setWindowTitle(winID, title):
    name = winapi.SetWindowText(winID, title)
    return name

#-----------------------------------------------------------------------
def setTopWindow(winID): 
    winapi.SetActiveWindow(winID)
    return winapi.SetForegroundWindow(winID)

#-----------------------------------------------------------------------
def getTopWindow():
    return winapi.GetForegroundWindow()

#-----------------------------------------------------------------------
def isTopWindow(winID):
    res = winapi.GetForegroundWindow()
    if winID == res:
      return True
    else:
      return False

#-----------------------------------------------------------------------
def moveWindow(winID, X,Y):
    res = winapi.SetWindowPos(winID, 0, X,Y, 0, 0, 0x0001)
    return res

#-----------------------------------------------------------------------
def resizeWindow(winID, W,H):
    WR = getWindowRect(winID)
    res = winapi.SetWindowPos(winID, 0, 0, 0, WR[0]+W, WR[1]+H, 0x0002)
    return res

#-----------------------------------------------------------------------
def getPixelColor(pos):
    (i_x, i_y) = pos
    hwnd = winapi.GetDesktopWindow()
    winDC = winapi.GetWindowDC(hwnd)
    color = winapi.GetPixel(winDC, i_x, i_y)
    rgb = (color & 0xff), ((color >> 8) & 0xff), ((color >> 16) & 0xff)
    winapi.ReleaseDC(hwnd, winDC)
    return rgb
  
#-----------------------------------------------------------------------
def setPixelColor(pos, color):
    (i_x, i_y) = pos
    hwnd = winapi.GetDesktopWindow()
    winDC = winapi.GetWindowDC(hwnd)
    rgb = ((color[2] & 0xff)<<16) | ((color[1] & 0xff)<<8) | (color[0] & 0xff)
    color = winapi.SetPixel(winDC, i_x, i_y, rgb)
    winapi.ReleaseDC(hwnd, winDC)
    return color


  