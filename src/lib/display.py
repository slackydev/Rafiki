#!/usr/bin/python
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

 --- Screen control for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
'''
This file is here for communication with the display-server, eather Windows or Linux. 
I will also place some functions here which is just a more "pythonic" renames of
other fuctions, that also allows for simpler access...
'''
from ..Interfaces import *

# ----- Renames ::
desktop_resolution = getDesktopScreenSize
resolution = getScreenSize

get_root = getRoot
get_window_rect = getWindowRect
get_window_by_name = getWindowByName
get_visible_windows = getVisibleWindows

window_from_pointer = getWindowFromPointer
window_from_point = getWindowFromPoint

get_pixel = getPixelColor
set_pixel = setPixelColor

grabscreen = grabScreen

get_window_text = getWindowTitle
set_window_text = setWindowTitle

set_top_window = setTopWindow
get_top_window = getTopWindow
is_top_window = isTopWindow

move_window = moveWindow
resize_window = resizeWindow


# ----- Workspace / Targetwindow ::
target = get_root() if int(sys.argv[1]) == 0 else int(sys.argv[1])
try:
    target_rect = get_window_rect(target)
except Exception:
    target = get_root()
    target_rect = get_window_rect(target)


#-------------------------------------------------------------------
def is_target_valid(wnd=target):
    try:
        get_window_text(wnd)
        return True
    except:
        return False

#-------------------------------------------------------------------
def get_target():
    return target

#-------------------------------------------------------------------
def get_target_rect():
    return target_rect

#-------------------------------------------------------------------
def get_target_size():
    _,_,W,H = target_rect
    return W,H

#-------------------------------------------------------------------
def set_target(wnd):
    global target, target_rect
    try:
        get_window_text(wnd)
        target = wnd
        target_rect = get_window_rect(target)
        return True
    except:
        return False

