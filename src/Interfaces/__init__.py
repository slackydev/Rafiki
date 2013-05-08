import sys
  
# If the user is on Windows
# Requirements: ---
if sys.platform == 'win32':
  from .mouse.windows import Mouse
  from .keybd.windows import Keybd
  from .screen.windows import *
  from .screen.prtscn_win import *

# We assume the user is on Linux
# Requirements: Python-Xlib
else:
  from .mouse.x11 import Mouse
  from .keybd.x11 import Keybd
  from .screen.x11 import *
  from .screen.prtscn_x11 import *