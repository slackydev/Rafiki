''' A few functions to go with Xlib '''
import os,sys
from Xlib import display, X
#import gtk.gdk
import Image
import struct

dsp = display.Display()
root = dsp.screen().root

def getScreenSize():
  W = dsp.screen().width_in_pixels
  H = dsp.screen().height_in_pixels
  return W,H

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
def getWindowByName(framename):
  atom = dsp.intern_atom('_NET_CLIENT_LIST') 
  windowIDs = root.get_full_property(atom, X.AnyPropertyType).value

  for winID in windowIDs:
    window = dsp.create_resource_object('window', winID)
    title = window.get_wm_name()
    if framename.lower() in title.lower():
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
def getWindowFromPointer():
  """ Simple function to get window from pointer - hardcoded 
  """
  pointer = root.query_pointer()
  x,y = pointer.root_x, pointer.root_y
  winID = pointer.child
  w = getWindowObjGeo(winID)
  SX, SY = w.x, w.y
  result = (w.x, w.y, w.x+w.width, w.y+w.height), winID

  # Get child frame
  children = winID.query_tree().children
  for child in children:
    c = getWindowObjGeo(child)
    if (c.width, c.height) > (1,1):
      attrs = child.get_attributes()
      if attrs.map_state == X.IsViewable:
        if (x >= (SX+c.x) and x <= (SX+c.x+c.width)) and \
           (y >= (SY+c.y) and y <= (SY+c.y+c.height)):
          result = ((SX+c.x), (SY+c.y), (SX+c.x+c.width), (SY+c.y+c.height)), child
          CX, CY = (SX+c.x), (SY+c.y)

          inner_children = child.query_tree().children
          for subchild in inner_children:
            # Child of child data (We wont go further - For now)
            ic = subchild.get_geometry()
            if (ic.width, ic.height) > (1,1):
              attrs = subchild.get_attributes()
              if attrs.map_state == X.IsViewable:
                if (x >= (CX+ic.x) and x <= (CX+ic.x+ic.width)) and \
                   (y >= (CY+ic.y) and y <= (CY+ic.y+ic.height)):

                  result = ((CX+ic.x), (CY+ic.y), \
                            (CX+ic.x+ic.width), (CY+ic.y+ic.height)), \
                            subchild

  return result


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
def get_pixel_colour(i_x, i_y):
  raw = root.get_image(i_x, i_y, 1, 1, X.ZPixmap, 0xffffffff)
  b,g,r = struct.unpack('<BBBB', raw.data)[0:3]
  return r,g,b


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
  import time

  image = GTK_grabscreen((0,0), (200,200))
  #image.show()

  time.sleep(2)

  '''
  data = root.query_pointer()
  x,y = data.root_x, data.root_y
  print get_pixel_colour(x, y)
  print getWindowFromPoint((x,y))
  #print get_pixel_colour(10, 10)
  '''