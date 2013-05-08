from ctypes import *

user32 = windll.user32
gdi32 = windll.gdi32

BOOL    = c_bool
INT     = c_int
LONG    = c_long
ULONG   = c_ulong
WORD    = c_ushort
LPVOID  = c_void_p

LPLONG = POINTER(LONG)


class POINT(Structure):
  _fields_ = [("x", ULONG), ("y", ULONG)]


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


''' --------- MOUSE AND KEYBD --------- '''
def SetMousePos(x,y):
  user32.GetCursorPos.argtypes = [LONG, LONG]
  user32.SetCursorPos(x, y)

def GetCursorPos():
  user32.GetCursorPos.argtypes = []
  pt = POINT()
  user32.GetCursorPos(byref(pt))
  return pt.x, pt.y

def mouse_event(vKey, dx, dy, dwData=0, dwExtraInfo=0):
  user32.mouse_event.argtypes = []
  user32.mouse_event(vKey, dx, dy, dwData, dwExtraInfo)

def LoadCursor(hInstance, cursorid):
  user32.LoadCursor.argtypes = []
  return user32.LoadCursor(hInstance, cursorid)

def SetCursor(hCursor):
  user32.SetCursor.argtypes = [LONG]
  win32api.SetCursor(hCursor)

def keybd_event(vKey, bScan=0, dwFlags=0, dwExtraInfo=0):
  user32.keybd_event.argtypes = []
  user32.keybd_event(vKey, bScan, dwFlags, dwExtraInfo)

def VkKeyScan(char):
  user32.VkKeyScan.argtypes = [WORD]
  return user32.VkKeyScan(char)

def GetAsyncKeyState(vKey):
  user32.GetAsyncKeyState.argtypes = [LONG]
  return user32.GetAsyncKeyState(vKey)

def GetKeyState(vKey):
  user32.GetKeyState.argtypes = [LONG]
  return user32.GetKeyState(vKey)


''' --------- CONNECT DESPLAY --------- '''
def GetSystemMetrics(i):
  user32.GetSystemMetrics.argtypes = [LONG]
  return user32.GetSystemMetrics(i)

def GetDisplaySize():
  user32.GetSystemMetrics.argtypes = [LONG]
  width = user32.GetSystemMetrics(0)
  height = user32.GetSystemMetrics(1)
  return width, height

def GetWindowRect(hwnd, rect):
  user32.GetWindowRect.argtypes = [LONG, LPLONG]
  return user32.GetWindowRect(hwnd, rect)

def WindowFromPoint(x_y):
  x,y = x_y;
  return user32.WindowFromPoint((x,y))

def GetDesktopWindow():
  user32.GetDesktopWindow.argtypes = []
  return user32.GetDesktopWindow()

def GetWindowDC(hwnd):
  user32.GetWindowDC.argtypes = [LONG]
  return user32.GetWindowDC(hwnd)

def GetPixel(dc, x, y):
  user32.GetPixel.argtypes = [LONG, LONG, LONG]
  return user32.GetPixel(dc, x, y)

def GetObject(hgdiobj, cbBuffer = None, lpvObject = None):
  _GetObject = gdi32.GetObjectA
  _GetObject.argtypes = [HGDIOBJ, INT, LPVOID]
  _GetObject.restype  = INT
  cbBuffer = sizeof(lpvObject)
  _GetObject(hgdiobj, cbBuffer, byref(lpvObject))
  return lpvObject

def GetBitmapBits(hbmp):
  _GetBitmapBits = gdi32.GetBitmapBits
  _GetBitmapBits.argtypes = [HGDIOBJ, LONG, LPVOID]
  _GetBitmapBits.restype  = LONG

  bitmap   = GetObject(hbmp, lpvObject = BITMAP())
  cbBuffer = bitmap.bmWidthBytes * bitmap.bmHeight
  lpvBits  = create_string_buffer("", cbBuffer)
  _GetBitmapBits(hbmp, cbBuffer, byref(lpvBits))
  return lpvBits.raw

def CreateCompatibleDC(WinDC):
  gdi32.CreateCompatibleDC.argtypes = [LONG]
  return gdi32.CreateCompatibleDC(WinDC)
   
def CreateCompatibleBitmap(winDC, W, H):
  gdi32.CreateCompatibleBitmap.argtypes = [LONG, LONG, LONG]
  return gdi32.CreateCompatibleBitmap(winDC, W, H)

def BitBlt(HDC, nXDest, nYDest, nWidth, nHeight, hdcSrc, nXSrc, nYSrc, dwRop):
  gdi32.BitBlt.argtypes = [LONG,LONG,LONG,LONG,LONG,LONG,LONG,LONG,LONG]
  return gdi32.BitBlt(HDC, nXDest, nYDest, nWidth, nHeight, hdcSrc, nXSrc, nYSrc, dwRop)

def SelectObject(HDC, bmp):
  gdi32.SelectObject.argtypes = [LONG, LONG]
  return gdi32.SelectObject(HDC, bmp)

def DeleteObject(obj):
  gdi32.DeleteObject.argtypes = [LONG]
  gdi32.DeleteObject(obj)

def DeleteDC(DC):
  gdi32.DeleteDC.argtypes = [LONG]
  gdi32.DeleteDC(DC)

def ReleaseDC(hwnd, winDC):
  user32.ReleaseDC.argtypes = [LONG, LONG]
  user32.ReleaseDC(hwnd, winDC)