#!/usr/bin/python
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 This file is part of the Rafiki Macro Library (RML)
 Copyright (c) 2012-2013 by Jarl Holta

 RML is free software: You can redistribute it and/or modify
 it under the terms of the wxWindows licence.

 RML is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

 wxWindows licence: <http://opensource.org/licenses/wxwindows.php>
 You might have recieved a copy of the lisence.

 --- Keyboard control for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
# For VKeys values (windows), see:
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd375731%28v=vs.85%29.aspx
#
# But it's preferable that you use keyboard.CODES['ENTER'] to get virtualkey
# That way, you know it works on both Linux, and Windows!

from random import randrange, uniform, gauss
from time import sleep
from ..Interfaces import Keybd

kbd = Keybd()

CODES = {
    'BACKSPACE':    kbd.backspace_key,
    'TAB':    		kbd.tab_key,
    'LINEFEED':		kbd.linefeed_key,
    'CLEAR':		kbd.clear_key,
    'RETURN':		kbd.return_key,
    'ENTER':		kbd.enter_key,
    'PAUSE':		kbd.pause_key,
    'SCROLL_LOCK':	kbd.scroll_lock_key,
    'SYS_REQ':    	kbd.sys_req_key,
    'ESCAPE':    	kbd.escape_key,
    'DELETE':    	kbd.delete_key,
    'SHIFT_L':    	kbd.shift_l_key,
    'SHIFT_R':    	kbd.shift_r_key,
    'SHIFT':    	kbd.shift_key,
    'ALT_L':    	kbd.alt_l_key,
    'ALT_R':    	kbd.alt_r_key,
    'ALT':    		kbd.alt_key,
    'CTRL_L':		kbd.control_l_key,
    'CTRL_R':		kbd.control_r_key,
    'CTRL':			kbd.control_key,
    'CAPS_LOCK':	kbd.caps_lock_key,
    'CAPITAL':    	kbd.capital_key,
    'META_l':   	kbd.meta_l_key,
    'META_R':    	kbd.meta_r_key,
    'SUPER_L':    	kbd.super_l_key,
    'WIN_L':    	kbd.windows_l_key,
    'SUPER_R':    	kbd.super_r_key,
    'WIN_R':    	kbd.windows_r_key,
    'HYPER_L':    	kbd.hyper_l_key,
    'HYPER_R':    	kbd.hyper_r_key,
    'HOME':    		kbd.home_key,
    'UP':    		kbd.up_key,
    'DOWN':    		kbd.down_key,
    'LEFT':    		kbd.left_key,
    'RIGHT':    	kbd.right_key,
    'END':    		kbd.end_key,
    'BEGIN':    	kbd.begin_key,
    'PAGE_UP':    	kbd.page_up_key,
    'PAGE_DOWN':    kbd.page_down_key,
    'PRIOR':    	kbd.prior_key,
    'NEXT':    		kbd.next_key,
    'SELECT':    	kbd.select_key,
    'PRINT':   		kbd.print_key,
    'PRINTSCREEN':	kbd.print_screen_key,
    'SNAPSHOT':		kbd.snapshot_key,
    'EXECUTE':    	kbd.execute_key,
    'INSERT':   	kbd.insert_key,
    'UNDO':    		kbd.undo_key,
    'REDO':    		kbd.redo_key,
    'MENU':    		kbd.menu_key,
    'APPS':   		kbd.apps_key,
    'FIND':    		kbd.find_key,
    'CANCEL':    	kbd.cancel_key,
    'HELP':    		kbd.help_key,
    'BREAK':    	kbd.break_key,
    'MODE_SWITCH':	kbd.mode_switch_key,
    'SCRIPT_SWITCH':kbd.script_switch_key,
    'NUM_LOCK':		kbd.num_lock_key
}

#-------------------------------------------------------------------
def wait_r(k,v):
    """ sleep everything for X time """
    time = round(uniform(k,v), 4)
    return sleep(time)

#-------------------------------------------------------------------
def key_down(key):
    """ press the key down
    """
    kbd.press_key(key)

#-------------------------------------------------------------------
def key_up(key):
    """ release / key up """
    kbd.release_key(key)

#-------------------------------------------------------------------
def press_key(key, times=1):
    """ Click the given key """
    inter = round(uniform(0.014,0.035), 4)
    kbd.tap_key(key, n=times, interval=inter)

#-------------------------------------------------------------------
def key_state(key):
    """ Return the current state of the key (0 or X) """
    return kbd.key_state(key)

#-------------------------------------------------------------------
def write_text(string, wpm=120):
    """ Click a series of buttons given as a string.
        Takes {SYMBOL}-keys as well

        @param: wpm: use your own speed (words per minute).
        -- http://en.wikipedia.org/wiki/Words_per_minute
    """
    wpm = max(wpm, 1)
    wait = 1.0 / ((wpm * 5.0) / 60.0)
    dyndev = ((wait*2)/6)+0.008

    if wait < dyndev: wait = dyndev
    minWait = wait-dyndev
    maxWait = minWait+0.016

    keys = str2keys(string)
    for key in keys:
      key_down(key)
      sleep(round(uniform(0.007, 0.015), 4))
      key_up(key)

      interval = round(uniform(minWait, minWait), 4)
      sleep(interval)

      ''' this will mess up the WPM a little... '''
      if randrange(0,6) == 0:
        sleep(interval * randrange(1,3))

#-------------------------------------------------------------------
def quick_write(string, ival=0.001):
    """ Click a series of buttons given as a string.
        Simple, and does not take symbol keys.
    """
    kbd.type_string(string, ival)

#-------------------------------------------------------------------
def str2keys(string):
    """ Convert {SYMBOL}-keys in to integers.
        Just leave normal chars alone.
    """
    chars = list(string)[::-1]
    keys = []

    while chars:
      char = chars.pop()
      
      if char == '{':
        name = []
        while char != '}':
          char = chars.pop()
          if char == '}':
            break
          name.append(char)

        code = ''.join(name)
        if code in CODES.keys():
          keys.append(CODES[code])
        else:
          keys.append('{')
          keys.extend(name)
          keys.append('}')

      else:
        keys.append(char)

    return keys
