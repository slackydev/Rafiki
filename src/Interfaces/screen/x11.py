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

 --- (Linux) Screen control for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
from Xlib import display, X, protocol
from Xlib.XK import string_to_keysym

#import gtk.gdk
from PIL import Image
import struct
import time

dsp = display.Display()
root = dsp.screen().root

#-----------------------------------------------------------------------
def getScreenSize():
    W = dsp.screen().width_in_pixels
    H = dsp.screen().height_in_pixels
    return W,H

#-----------------------------------------------------------------------  
def getDesktopScreenSize():
    try:
        prime = root.xrandr_get_screen_info()._data['sizes'][1]
        size = prime['width_in_pixels'], prime['height_in_pixels']
    except:
        size = getScreenSize()
    return size

#-----------------------------------------------------------------------
def getRoot():
    window = root.id
    return window

#-----------------------------------------------------------------------
def getWindowParent(winID):
    window = dsp.create_resource_object('window', winID)
    return window.query_tree().parent

#-----------------------------------------------------------------------
def getWindowChildren(winID):
    window = dsp.create_resource_object('window', winID)
    children = window.query_tree().children
    return children

#-----------------------------------------------------------------------
def getWindowGeo(winID):
    window = dsp.create_resource_object('window', winID)
    return window.get_geometry()

#-----------------------------------------------------------------------
def getWindowObjGeo(win):
    return win.get_geometry()

#-----------------------------------------------------------------------
def getWindowByName(title):
    atom = dsp.intern_atom('_NET_CLIENT_LIST') 
    windowIDs = root.get_full_property(atom, X.AnyPropertyType).value

    for winID in windowIDs:
      window = dsp.create_resource_object('window', winID)
      wndtitle = window.get_wm_name()
      if title.lower() in wndtitle.lower():
        return winID

#-----------------------------------------------------------------------
def getVisibleWindows():
    """ Not the quickest function, but it does the job quite well!
    """
    ''' query_tree returns the windows as a tree - as seen by the user '''
    windows = root.query_tree().children
    result = []

    def wrapped(obj, name, pos, size):
      ID = obj.id if isinstance(obj.id, int) else obj.id.id
      if size > (1,1) and pos >= (0,0):
        result.append({'obj':  ID, 
                       'name': name,
                       'pos':  pos,
                       'size': size})
          
      children = obj.query_tree().children
      for child in children:
        attrs = child.get_attributes()
        if attrs.map_state == X.IsViewable:
          p = child.get_geometry()
          wrapped(obj  = child, 
                  name = child.get_wm_name(), 
                  pos  = (pos[0]+p.x, pos[1]+p.y), 
                  size = (p.width, p.height))
          

    for wnd_id in windows:
      wnd = dsp.create_resource_object('window', wnd_id)
      attrs = wnd.get_attributes()
      if attrs.map_state == X.IsViewable:
        f = wnd.id.get_geometry()
        name = wnd.get_wm_name() if wnd.get_wm_name() != None else 'Frame'
        wrapped(obj  = wnd, 
                name = name, 
                pos  = (f.x, f.y),
                size = (f.width, f.height))

    return result

#-----------------------------------------------------------------------
def getWindowRect(winID):
    window = dsp.create_resource_object('window', winID)
    geo = window.get_geometry()
    gpos = [geo.x,  geo.y]
    def wrapped(obj):
      par = obj.query_tree().parent
      if par:
        p = par.get_geometry()
        gpos[0] += p.x
        gpos[1] += p.y
        wrapped(par)
    
    wrapped(window)
    return (gpos[0], gpos[1], geo.width, geo.height)

#-----------------------------------------------------------------------
def getWindowFromPointer():
    """ find current window behind pointer -- we assume that 
        `getVisibleWindows()` returns the windows in correct order!
    """
    pointer = root.query_pointer()
    i_x, i_y = pointer.root_x, pointer.root_y
    windows = reversed(getVisibleWindows())
    for wnd in windows:
      xs,ys = wnd['pos']
      xe,ye = wnd['size'][0]+xs, wnd['size'][1]+ys
      if (i_x >= xs) and (i_x <= xe) and \
         (i_y >= ys) and (i_y <= ye):
        return wnd


#-----------------------------------------------------------------------
def getWindowFromPoint(point, skipz=[]):
    """ find current window behind i_x, i_y -- we assume that 
        `getVisibleWindows()` returns the windows in correct order!
    """
    i_x, i_y = point
    windows = reversed(getVisibleWindows())
    for wnd in windows:
      xs,ys = wnd['pos']
      xe,ye = wnd['size'][0]+xs, wnd['size'][1]+ys
      if (i_x >= xs) and (i_x <= xe) and \
         (i_y >= ys) and (i_y <= ye):
        if wnd['obj'] in skipz: continue

        return wnd

#-----------------------------------------------------------------------
def getWindowTitle(winID):
    window = dsp.create_resource_object('window', winID)
    title = window.get_wm_name()
    return title

#-----------------------------------------------------------------------
def setWindowTitle(winID, title):
    ''' Not changing the visual name 
        @todo: fix
    '''
    window = dsp.create_resource_object('window', winID)
    window.set_wm_name(title)
    dsp.flush()
    return window.get_wm_name()

#-----------------------------------------------------------------------
def setTopWindow(winID):
    win = dsp.create_resource_object('window', winID)
    #win.set_input_focus(X.RevertToParent, X.CurrentTime)
    #win.configure(stack_mode=X.TopIf)
    clientmessage = protocol.event.ClientMessage(
        window=win,
        client_type=dsp.intern_atom('_NET_ACTIVE_WINDOW'),
        data=(32, (2, X.CurrentTime, 0, 0, 0))
    )
    mask = (X.SubstructureRedirectMask|X.SubstructureNotifyMask)
    root.send_event(clientmessage, event_mask=mask) 
    dsp.flush()
    return True

#-----------------------------------------------------------------------
def getTopWindow():
    atom = dsp.intern_atom('_NET_ACTIVE_WINDOW') 
    window = root.get_full_property(atom, X.AnyPropertyType).value
    return window[0]

#-----------------------------------------------------------------------
def isTopWindow(winID):
    atom = dsp.intern_atom('_NET_ACTIVE_WINDOW') 
    window = root.get_full_property(atom, X.AnyPropertyType).value
    if winID == window[0]:
      return True
    else:
      return False

#-----------------------------------------------------------------------
def moveWindow(winID, X,Y):
    win = dsp.create_resource_object('window', winID)
    win.configure(x=X, y=Y)
    dsp.flush()

#-----------------------------------------------------------------------
def resizeWindow(winID, W,H):
    win = dsp.create_resource_object('window', winID)
    R = getWindowRect(winID)
    win.configure(width=W, height=H)
    dsp.flush()

#-----------------------------------------------------------------------
def getPixelColor(pos):
    (i_x, i_y) = pos
    raw = root.get_image(i_x, i_y, 1, 1, X.ZPixmap, 0xffffffff)
    b,g,r = struct.unpack('<BBBB', raw.data)[0:3]
    return r,g,b

#-----------------------------------------------------------------------
def setPixelColor(pos, color):
    (i_x, i_y) = pos
    r,g,b = color
    screen = dsp.screen()
    colormap = screen.default_colormap
    color = colormap.alloc_color(r*r, g*g, b*b).pixel
    GC = screen.root.create_gc(foreground = color,
                               subwindow_mode = X.IncludeInferiors)

    screen.root.point(GC, i_x, i_y)
    dsp.sync()

#-----------------------------------------------------------------------
def drawRect(width, pos, size):
    ''' Draw a rectangle '''
    screen = dsp.screen()

    colormap = screen.default_colormap
    color = colormap.alloc_color(0, 0, 0)
    xor_color = color.pixel ^ 0xffffff 

    GC = screen.root.create_gc(
        line_width = width,
        line_style = X.LineSolid,
        fill_style = X.FillOpaqueStippled,
        fill_rule  = X.WindingRule,
        cap_style  = X.CapButt,
        join_style = X.JoinMiter,
        foreground = xor_color,
        background = screen.black_pixel,
        function = X.GXxor, 
        graphics_exposures = False,
        subwindow_mode = X.IncludeInferiors
      )

    x,y = pos 
    W,H = size
    screen.root.rectangle(GC, x-1,y-1, W+1,H+1)
    dsp.sync()

#-----------------------------------------------------------------------
def drawTargetArea(maxTimer=20, line_width=3):
    ''' Draw the area box under the mouse '''
    def get_key_state(key):
        keysym = string_to_keysym(key)
        keycode = dsp.keysym_to_keycode(keysym)
        if(keycode == 0): return 0
        keys = dsp.query_keymap()
        return (keys[keycode >> 3] >> (keycode & 0x07)) & 0x01

    pointer = root.query_pointer()
    i_x, i_y = pointer.root_x, pointer.root_y
    window = getWindowFromPoint((i_x, i_y))
    prev_pos = window['pos']
    prev_obj = window['obj']
    prev_size = window['size']
    drawRect(line_width, prev_pos,prev_size)

    start = time.time()
    while True:
        pointer = root.query_pointer()
        i_x, i_y = pointer.root_x, pointer.root_y
        window = getWindowFromPoint((i_x, i_y))
        pos = window['pos']
        obj = window['obj']
        size = window['size']

        if obj!=prev_obj:
            drawRect(line_width, prev_pos, prev_size)
            dsp.flush()
            drawRect(line_width, pos,size)

        prev_obj = obj
        prev_pos = pos
        prev_size = size

        state_ctrl = get_key_state('Control_L')
        state_t    = get_key_state('W')
        if state_t != 0 and state_ctrl != 0:
            break

        if (start+maxTimer) < time.time():
            break

    drawRect(line_width, prev_pos, prev_size)
    return prev_obj

#-----------------------------------------------------------------------
'''
def GTK_grabscreen(pos=(0,0), size=(0,0)):
  root = gtk.gdk.get_default_root_window()
  sz = root.get_size()
  x,y = pos
  W,H = size[0]+x, size[1]+y

  if W>sz[0] or W<=0: W = sz[0]
  if H>sz[1] or H<=0: H = sz[1]

  if x<0: x = 0
  if y<0: y = 0
       
  pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, W,H)
  pb = pb.get_from_drawable(root, root.get_colormap(), x,y, 0,0, W,H)
  if (pb != None):
    return Image.fromstring("RGB", (W,H), pb.get_pixels())
  else:
    return False
'''

#-----------------------------------------------------------------------
# Test
if __name__ == '__main__':
  print drawTargetArea(1, 4)
  
  '''
  data = root.query_pointer()
  x,y = data.root_x, data.root_y
  print get_pixel_colour(x, y)
  print getWindowFromPoint((x,y))
  #print get_pixel_colour(10, 10)
  '''
