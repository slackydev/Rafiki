import ctypes
import os, sys
import Image
from Xlib import display

LibName = 'prtscn_dll_x11.so'
AbsLibPath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + LibName
grab = ctypes.CDLL(AbsLibPath)

dsp = display.Display(None)
geo = dsp.screen().root.get_geometry()

def grabScreen(x1,y1,x2,y2):
	x1,y1 = max(x1, 0), max(y1, 0)
	if x2 > geo.width: x2 = geo.width
	if y2 > geo.height: y2 = geo.height

	W, H = min(x2-x1, geo.width), min(y2-y1, geo.height)

	if W < 0: W = 1
	if H < 0: H = 1

	size = W * H
	objlength = size * 3

	grab.getScreen.argtypes = []
	result = (ctypes.c_ubyte*objlength)()

	grab.getScreen(x1,y1, W, H, result)
	return Image.frombuffer('RGB', (W, H), result, 'raw', 'RGB', 0, 1)
	

if __name__ == '__main__':
  import time
  for i in range(100):
  	im = grabScreen(228,58,278,70)
  #im.show()


