import platform
  
# If the user is on Windows
# Requirements: None
if platform.system() == 'Windows':
    from .mouse.windows import Mouse
    from .keybd.windows import Keybd
    from .screen.windows import *
    from .screen.prtscn_win import *

# If the user is on Linux
# Requirements: Python-Xlib
elif platform.system() == 'Linux':
    from .mouse.x11 import Mouse
    from .keybd.x11 import Keybd
    from .screen.x11 import *
    from .screen.prtscn_x11 import *

else:
	pass
	#Should raise an unsupported OS exception...