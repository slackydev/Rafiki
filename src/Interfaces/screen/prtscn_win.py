'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 Only written if for windows as it's now, but I might just take a 
 look at some standard linux API's / Frameworks. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
import Image
import ctypes
from ctypes.wintypes import HGDIOBJ

user32 = ctypes.windll.user32       
gdi32 = ctypes.windll.gdi32

SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
SRCCOPY = 13369376

BOOL    = ctypes.c_bool
INT   = ctypes.c_int
LONG    = ctypes.c_long
WORD    = ctypes.c_ushort
LPVOID  = ctypes.c_void_p
Structure = ctypes.Structure

LPLONG = ctypes.POINTER(LONG)

class BITMAP(Structure):
    _fields_ = [
        ("bmType",          LONG),
        ("bmWidth",         LONG),
        ("bmHeight",        LONG),
        ("bmWidthBytes",    LONG),
        ("bmPlanes",        WORD),
        ("bmBitsPixel",     WORD),
        ("bmBits",          LPVOID),
    ]

def GetObject(hgdiobj, cbBuffer = None, lpvObject = None):
    _GetObject = gdi32.GetObjectA
    _GetObject.argtypes = [HGDIOBJ, INT, LPVOID]
    _GetObject.restype  = INT
    cbBuffer = ctypes.sizeof(lpvObject)
    _GetObject(hgdiobj, cbBuffer, ctypes.byref(lpvObject))
    return lpvObject

def GetBitmapBits(hbmp):
    _GetBitmapBits = gdi32.GetBitmapBits
    _GetBitmapBits.argtypes = [HGDIOBJ, LONG, LPVOID]
    _GetBitmapBits.restype  = LONG

    bitmap   = GetObject(hbmp, lpvObject = BITMAP())
    cbBuffer = bitmap.bmWidthBytes * bitmap.bmHeight
    lpvBits  = ctypes.create_string_buffer("", cbBuffer)
    _GetBitmapBits(hbmp, cbBuffer, ctypes.byref(lpvBits))
    return lpvBits.raw

    
def grabScreen(x1,y1,x2,y2):
    # Argumentlist:    
    user32.GetDesktopWindow.argtypes = []
    user32.GetSystemMetrics.argtypes = [LONG]
    user32.GetWindowDC.argtypes = [LONG]
    gdi32.CreateCompatibleDC.argtypes = [LONG]
    gdi32.CreateCompatibleBitmap.argtypes = [LONG, LONG, LONG]
    gdi32.SelectObject.argtypes = [LONG, LONG]
    gdi32.BitBlt.argtypes = [LONG,LONG,LONG,LONG,LONG,LONG,LONG,LONG,LONG]
    gdi32.DeleteObject.argtypes = [LONG]
    gdi32.DeleteDC.argtypes = [LONG]
    user32.ReleaseDC.argtypes = [LONG, LONG]
    
    # The calls to winapi
    hwnd = user32.GetDesktopWindow()
    hwnd = LONG(hwnd)
    
    width = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
    height = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)

    x1,y1 = max(x1, 0), max(y1, 0)
    if x2 > width: x2 = width
    if y2 > height: y2 = height

    W, H = min(x2-x1, width), min(y2-y1, height)

    if W < 0: W = 1
    if H < 0: H = 1

    winDC = user32.GetWindowDC(hwnd)
    cDC = gdi32.CreateCompatibleDC(winDC)
    bmp = gdi32.CreateCompatibleBitmap(winDC, W, H)
    gdi32.SelectObject(cDC, bmp)
    gdi32.BitBlt(cDC, 0,0, W,H, winDC, x1,y1, SRCCOPY)
  
    # Image from bitmapbuffer
    rawbmp = GetBitmapBits(bmp)

    #Destroy all objects!
    gdi32.DeleteObject(gdi32.SelectObject(cDC, bmp))
    gdi32.DeleteDC(cDC)
    user32.ReleaseDC(hwnd, winDC)
    
    return Image.frombuffer('RGB', (W, H), rawbmp, 'raw', 'BGRX', 0, 1)

if __name__ == '__main__':
  im = grabScreen(0,0,1440,900)
  im.show()