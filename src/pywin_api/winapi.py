from ctypes import *
from ctypes.wintypes import HGDIOBJ

user32 = windll.user32
gdi32 = windll.gdi32
kernel32 = windll.kernel32

BYTE    = c_ubyte
BOOL    = c_bool
INT     = c_int
LONG    = c_long
ULONG   = c_ulong
TCHAR   = c_wchar
WORD    = c_ushort
DWORD   = c_ulong
WPARAM  = DWORD
LPVOID  = c_void_p
LPLONG  = POINTER(LONG)
LPSTR   = c_char_p
LPTSTR  = c_wchar_p
HWND    = LPVOID
LPARAM  = LPVOID
LRESULT = LPVOID


class POINT(Structure):
    _fields_ = [
        ("x", ULONG), 
        ("y", ULONG)
    ]
    
class RECT(Structure):
    _fields_ = [
        ("x1", ULONG), 
        ("y1", ULONG),
        ("x2", ULONG),
        ("y2", ULONG)
    ]

#-------
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

#-------
def GetLastError():
    _GetLastError = kernel32.GetLastError
    _GetLastError.argtypes = []
    _GetLastError.restype  = DWORD
    return _GetLastError()
    
#-------
def SetLastError(dwErrCode):
    _SetLastError = kernel32.SetLastError
    _SetLastError.argtypes = [DWORD]
    _SetLastError.restype  = None
    _SetLastError(dwErrCode)
    
    
''' ------------------------ MOUSE AND KEYBD ------------------------ '''
def SetCursorPos(x,y):
  user32.SetCursorPos.argtypes = [INT, INT]
  user32.SetCursorPos(x, y)
  
#------------------------------------------------------------------------
def GetCursorPos():
  user32.GetCursorPos.argtypes = [POINTER(POINT)]
  pt = POINT()
  user32.GetCursorPos(byref(pt))
  return pt.x, pt.y

#------------------------------------------------------------------------
def mouse_event(vKey, dx, dy, dwData=0, dwExtraInfo=0):
  user32.mouse_event.argtypes = [DWORD,DWORD,DWORD,DWORD,LPVOID]
  user32.mouse_event(vKey, dx, dy, dwData, dwExtraInfo)

#------------------------------------------------------------------------
def LoadCursor(hInstance, cursorid):
  user32.LoadCursor.argtypes = [LONG,LONG]
  return user32.LoadCursor(hInstance, cursorid)
  
#------------------------------------------------------------------------
def SetCursor(hCursor):
  user32.SetCursor.argtypes = [LONG]
  win32api.SetCursor(hCursor)
  
#------------------------------------------------------------------------
def keybd_event(vKey, bScan=0, dwFlags=0, dwExtraInfo=0):
  user32.keybd_event.argtypes = [BYTE,BYTE,DWORD,LPVOID]
  user32.keybd_event(vKey, bScan, dwFlags, dwExtraInfo)
  
#------------------------------------------------------------------------
def VkKeyScan(char):
  user32.VkKeyScanW.argtypes = [TCHAR]
  return user32.VkKeyScanW(char)
  
#------------------------------------------------------------------------
def GetAsyncKeyState(vKey):
  user32.GetAsyncKeyState.argtypes = [LONG]
  return user32.GetAsyncKeyState(vKey)
  
#------------------------------------------------------------------------
def GetKeyState(vKey):
  user32.GetKeyState.argtypes = [LONG]
  return user32.GetKeyState(vKey)
  

''' ------------------------ CONNECT DESPLAY ------------------------ '''
def GetSystemMetrics(SM):
  user32.GetSystemMetrics.argtypes = [LONG]
  return user32.GetSystemMetrics(SM)
  
#------------------------------------------------------------------------
def GetDisplaySize():
  user32.GetSystemMetrics.argtypes = [LONG]
  width = user32.GetSystemMetrics(0)
  height = user32.GetSystemMetrics(1)
  return width, height
  
#------------------------------------------------------------------------  
def GetVirtualDisplaySize():
  user32.GetSystemMetrics.argtypes = [LONG]
  width = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
  height = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
  return width, height
  
#------------------------------------------------------------------------
def GetWindow(hWnd, uCmd):
    user32.GetParent.argtypes = [HWND, INT]
    return user32.GetWindow(hWnd, uCmd)
 
#------------------------------------------------------------------------ 
def GetWindowLong(hwnd, index):
    user32.GetWindowLongW.argtypes = [HWND, INT]
    return user32.GetWindowLongW(hwnd, index)
  
#------------------------------------------------------------------------
def GetWindowRect(hwnd):
  user32.GetWindowRect.argtypes = [HWND, POINTER(RECT)]
  rect = RECT()
  user32.GetWindowRect(hwnd, byref(rect))
  return rect.x1, rect.y1, rect.x2, rect.y2
  
#------------------------------------------------------------------------
def WindowFromPoint(point):
  user32.WindowFromPoint.argtype = [POINT]
  point = POINT(*point)
  return user32.WindowFromPoint(point)
  
#------------------------------------------------------------------------
def GetDesktopWindow():
  user32.GetDesktopWindow.argtypes = []
  return user32.GetDesktopWindow()
  
#------------------------------------------------------------------------
def GetWindowDC(hwnd):
  user32.GetWindowDC.argtypes = [HWND]
  return user32.GetWindowDC(hwnd)
  
#------------------------------------------------------------------------
def GetParent(hwnd):
    user32.GetParent.argtypes = [HWND]
    return user32.GetParent(hwnd)
    
#------------------------------------------------------------------------
def IsWindowVisible(hwnd): 
    user32.IsWindowVisible.argtypes = [HWND]
    res = user32.IsWindowVisible(hwnd)   
    return res

#------------------------------------------------------------------------
class WindowEnumerator(object):
    """
    Window enumerator class.  You can pass it's instances
    as callback functions in window enumeration APIs.
    """
    def __init__(self):
        self.hwnd = []

    def __call__(self, hwnd, lParam):
        self.hwnd.append(hwnd)
        return True
  
#------------------------------------------------------------------------
class __EnumWndProc(WindowEnumerator):
    pass
    
#------------------------------------------------------------------------  
def EnumWindows():
    WNDENUMPROC = WINFUNCTYPE(BOOL,HWND,LPARAM)
    _EnumWindows = user32.EnumWindows
    _EnumWindows.argtypes = [WNDENUMPROC, LPARAM]
    _EnumWindows.restype  = BOOL

    EnumFunc = __EnumWndProc()
    lpEnumFunc = WNDENUMPROC(EnumFunc)
    if not _EnumWindows(lpEnumFunc, None):
        errcode = GetLastError()
        if errcode not in (ERROR_NO_MORE_FILES, ERROR_SUCCESS):
            raise WinError(errcode)
    return EnumFunc.hwnd
    
#------------------------------------------------------------------------    
def GetWindowTextLength(hwnd):
    user32.GetWindowTextLengthW.argtypes = [HWND]
    length = user32.GetWindowTextLengthW(hwnd)
    return length
    
#------------------------------------------------------------------------    
def GetWindowText(hwnd):
    length = GetWindowTextLength(hwnd)
    if not length: return False
    buff = create_unicode_buffer(length + 1)
    user32.GetWindowTextW.argtypes = [HWND, LPTSTR, INT]
    res = user32.GetWindowTextW(hwnd, buff, length + 1)   
    if res: return buff.value
    else: return False  
  
#------------------------------------------------------------------------    
def SetWindowText(hwnd, text):
    user32.SetWindowTextW.argtypes = [HWND, LPTSTR]
    res = user32.SetWindowTextW(hwnd, LPTSTR(text)) 
    return res
  
#------------------------------------------------------------------------    
def GetActiveWindow():
    user32.GetActiveWindow.argtypes = []
    res = user32.GetActiveWindow()   
    return res
    
#------------------------------------------------------------------------    
def SetActiveWindow(hwnd):
    user32.SetActiveWindow.argtypes = [HWND]
    res = user32.SetActiveWindow(hwnd)   
    return res
    
#------------------------------------------------------------------------    
def BringWindowToTop(hwnd):
    user32.BringWindowToTop.argtypes = [HWND]
    res = user32.BringWindowToTop(hwnd)   
    return res

#------------------------------------------------------------------------      
def SetForegroundWindow(hwnd):
    user32.SetForegroundWindow.argtypes = [HWND]
    res = user32.SetForegroundWindow(hwnd)   
    return res

#------------------------------------------------------------------------      
def GetForegroundWindow():
    user32.GetForegroundWindow.argtypes = []
    res = user32.GetForegroundWindow()   
    return res
    
#------------------------------------------------------------------------    
def GetTopWindow(hwnd=0):
    user32.GetTopWindow.argtypes = [HWND]
    res = user32.GetTopWindow(hwnd)   
    return res
    
#------------------------------------------------------------------------    
def SetWindowPos(hwnd, param1, x,y,cx,cy, param2):    
    user32.SetWindowPos.argtypes = [HWND, LPARAM, INT,INT,INT,INT, LPARAM]
    res = user32.SetWindowPos(hwnd, param1, x,y,cx,cy, param2)   
    return res
    
    
''' ---------------------- UNCATEGORIZED STUFF ---------------------- '''     
#------------------------------------------------------------------------
def GetObject(hgdiobj, cbBuffer = None, lpvObject = None):
  _GetObject = gdi32.GetObjectA
  _GetObject.argtypes = [HGDIOBJ, INT, LPVOID]
  _GetObject.restype  = INT
  cbBuffer = sizeof(lpvObject)
  _GetObject(hgdiobj, cbBuffer, byref(lpvObject))
  return lpvObject
  
#------------------------------------------------------------------------
def GetBitmapBits(hbmp):
  _GetBitmapBits = gdi32.GetBitmapBits
  _GetBitmapBits.argtypes = [HGDIOBJ, LONG, LPVOID]
  _GetBitmapBits.restype  = LONG

  bitmap   = GetObject(hbmp, lpvObject = BITMAP())
  cbBuffer = bitmap.bmWidthBytes * bitmap.bmHeight
  lpvBits  = create_string_buffer("", cbBuffer)
  _GetBitmapBits(hbmp, cbBuffer, byref(lpvBits))
  return lpvBits.raw
  
#------------------------------------------------------------------------
def CreateCompatibleDC(WinDC):
  gdi32.CreateCompatibleDC.argtypes = [LONG]
  return gdi32.CreateCompatibleDC(WinDC)
  
#------------------------------------------------------------------------  
def CreateCompatibleBitmap(winDC, W, H):
  gdi32.CreateCompatibleBitmap.argtypes = [LONG, LONG, LONG]
  return gdi32.CreateCompatibleBitmap(winDC, W, H)
  
#------------------------------------------------------------------------
def BitBlt(HDC, nXDest, nYDest, nWidth, nHeight, hdcSrc, nXSrc, nYSrc, dwRop):
  gdi32.BitBlt.argtypes = [LONG,LONG,LONG,LONG,LONG,LONG,LONG,LONG,LONG]
  return gdi32.BitBlt(HDC, nXDest, nYDest, nWidth, nHeight, hdcSrc, nXSrc, nYSrc, dwRop)
  
#------------------------------------------------------------------------
def SelectObject(HDC, bmp):
  gdi32.SelectObject.argtypes = [LONG, LONG]
  return gdi32.SelectObject(HDC, bmp)

#------------------------------------------------------------------------
def GetPixel(dc, x, y):
  gdi32.GetPixel.argtypes = [LONG, LONG, LONG]
  color = gdi32.GetPixel(dc, x, y)
  return color
  
#------------------------------------------------------------------------
def SetPixel(dc, x, y, color):
  gdi32.SetPixel.argtypes = [LONG, LONG, LONG, LONG]
  color = gdi32.SetPixel(dc, x, y, color)
  return color
  
  
''' ------------------------ REMOVE N DELETE ------------------------ '''  
#------------------------------------------------------------------------
def DeleteObject(obj):
  gdi32.DeleteObject.argtypes = [LONG]
  gdi32.DeleteObject(obj)
  
#------------------------------------------------------------------------
def DeleteDC(DC):
  gdi32.DeleteDC.argtypes = [LONG]
  gdi32.DeleteDC(DC)
  
#------------------------------------------------------------------------
def ReleaseDC(hwnd, winDC):
  user32.ReleaseDC.argtypes = [HWND, LONG]
  user32.ReleaseDC(hwnd, winDC)