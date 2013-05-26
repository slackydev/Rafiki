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

 --- Take a screenshot, crop it and (and other mods?) - Then save it ---                                            
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
import wx
import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Interfaces import *
from PIL import Image

ID_WORK = wx.NewId()
ID_SHOOT = 0
ID_SAVE = 1
ID_NEW = 2
ID_NEW = 3
ID_NEW = 4

#Set current working dir here..
os.chdir(sys.path[0])
ICONS = '../icons/'

def ShowOptions(parent):
  """Shows the frame"""
  if parent != None:
    if PrtscnFrame.INSTANCE is None:
      PRTSCN = PrtscnFrame(parent, ("Rafiki - Printscreen"))
    else:
      PrtscnFrame.INSTANCE.Destroy()
      PrtscnFrame.INSTANCE = None

#-----------------------------------------------------------------------------#
class PrtscnFrame(wx.Frame):
  INSTANCE = None
  def __init__(self, parent, title):
    style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
    wx.Frame.__init__(self, parent, wx.ID_ANY, title, style=style)
    
    #Toolbar...
    Toolbar(self)

    # Attributes
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(WorkerPanel(self, ID_WORK), 1, wx.EXPAND)
    self.SetSizer(sizer)

    self.SetMinSize((550,380))

    if parent:
        self.CentreOnParent(wx.BOTH)

    #Statusbar
    self.CreateStatusBar(1)

    #Show
    self.Show(True)

    # Event Handlers
    self.Bind(wx.EVT_CLOSE, self.OnClose)
  
  def __new__(self, *args, **kargs):
    #--------------------------------------------------------------------------
    """Create the instance"""
    if self.INSTANCE is None:
       self.INSTANCE = wx.Dialog.__new__(self, *args, **kargs)
    return self.INSTANCE

  def Destroy(self):
    #--------------------------------------------------------------------------
    """Destroy the instance"""
    self.__class__.INSTANCE = None
    wx.Dialog.Destroy(self)

  def OnClose(self, evt):
    #--------------------------------------------------------------------------
    """Cleanup settings on close"""
    PrtscnFrame.INSTANCE = None
    evt.Skip()


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| WorkerPanel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
#-===========================================================================-#
class WorkerPanel(wx.PyPanel):
  #--------------------------------------------------------------------------
  """Creates the "drawingboard" and menus to go
  @todo: Everything!
  """
  def __init__(self, parent, id_):
    """ Initialiases the interface """
    wx.PyPanel.__init__(self, parent, id_)
    self.parent = parent
    self._layout()

    self.Bind(wx.EVT_PAINT, self.OnPaint)
    

  def _layout(self):
    #--------------------------------------------------------------------------
    self.SetMinSize((380,-1))

  def OnPaint(self, event=None):
    dc = wx.PaintDC(self)
    dc.Clear()
    #dc.SetPen(wx.Pen(wx.BLACK, 3))
    #dc.DrawLine(0, 0, 150, 100)

    im_W,im_H = getScreenSize()
    im = grabScreen(0,0, im_W, im_H)
    self.NH = 315
    self.NW = int(im.size[0]*(float(self.NH)/im.size[1]))
    im = im.resize((self.NW, self.NH), Image.BILINEAR)
    image = wx.EmptyImage(im.size[0], im.size[1])
    image.SetData(im.tostring())

    image = wx.BitmapFromImage(image)
    dc.DrawBitmap(image, 0, 0)


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| This class defines the toolbar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class Toolbar:
  #----------------------------------------------------------------------
  def __init__(self, rafiki):
    toolbar = rafiki.CreateToolBar()

    ''' FILE MENU '''
    toolbar.AddSimpleTool(ID_SHOOT, wx.Image(ICONS + 'document-new.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Screenshot', 'Take a new screenshot')

    toolbar.AddSimpleTool(ID_SAVE, wx.Image(ICONS + 'document-save.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save', 'Save your current image')

    toolbar.AddSeparator()

    toolbar.Realize()



#-===========================================================================-#
# Test
if __name__ == '__main__':
    APP = wx.App(False)
    PRTSCN = PrtscnFrame(None, ("Printscreen"))
    APP.MainLoop()