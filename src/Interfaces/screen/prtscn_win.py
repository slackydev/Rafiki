'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 Only written if for windows as it's now, but I might just take a 
 look at some standard linux API's / Frameworks. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
import os,sys
abspath = os.path.abspath(__file__)
srcpath = os.path.dirname(abspath)+os.sep+'..'+os.sep+'..'
sys.path.insert(1, srcpath)

from PIL import Image
from pywin_api.conn import *
from pywin_api import winapi

def grabScreen(x1,y1,x2,y2):
    # The calls to winapi
    hwnd = winapi.GetDesktopWindow()
    
    width = winapi.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    height = winapi.GetSystemMetrics(SM_CYVIRTUALSCREEN)

    x1,y1 = max(x1, 0), max(y1, 0)
    if x2 > width: x2 = width
    if y2 > height: y2 = height

    W, H = min(x2-x1, width), min(y2-y1, height)

    if W < 0: W = 1
    if H < 0: H = 1

    winDC = winapi.GetWindowDC(hwnd)
    cDC = winapi.CreateCompatibleDC(winDC)
    bmp = winapi.CreateCompatibleBitmap(winDC, W, H)
    winapi.SelectObject(cDC, bmp)
    winapi.BitBlt(cDC, 0,0, W,H, winDC, x1,y1, SRCCOPY)
  
    # Image from bitmapbuffer
    rawbmp = winapi.GetBitmapBits(bmp)

    #Destroy all objects!
    winapi.DeleteObject(winapi.SelectObject(cDC, bmp))
    winapi.DeleteDC(cDC)
    winapi.ReleaseDC(hwnd, winDC)
    
    return Image.frombuffer('RGB', (W, H), rawbmp, 'raw', 'BGRX', 0, 1)

if __name__ == '__main__':
  im = grabScreen(0,0,1440,900)
  im.show()