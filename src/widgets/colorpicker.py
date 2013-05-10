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

 --- Colorpicker as used in the GUI ---                                            
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
import wx
from PIL import Image, ImageDraw
import os, sys
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from Interfaces import *

mouse = Mouse()
ID_PICKER = wx.NewId()

def ShowPicker(parent):
  """Shows the calculator"""
  if parent != None:
    if PickerFrame.INSTANCE is None:
      PICKER = PickerFrame(parent, ("Rafiki | Colorpicker"))
      PICKER.Show(True)
    else:
      PickerFrame.INSTANCE.Destroy()
      PickerFrame.INSTANCE = None

#-----------------------------------------------------------------------------#

class PickerFrame(wx.MiniFrame):
  """Create the calculator. Only a single instance can exist at
  any given time.
  """
  INSTANCE = None
  def __init__(self, parent, title):
    """Initialize the calculator frame"""
    wx.MiniFrame.__init__(self, parent, title=title,
                          style=wx.DEFAULT_DIALOG_STYLE)
        
    # Attributes
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(PickerPanel(self, ID_PICKER), 1, wx.ALL|wx.EXPAND)
    self.SetSizer(sizer)
    self.SetInitialSize()
    self.CentreOnParent(wx.BOTH)

    # Event Handlers
    self.Bind(wx.EVT_CLOSE, self.OnClose)

  
  def __new__(self, *args, **kargs):
    #----------------------------------------------------------------------------
    """Create the instance"""
    if self.INSTANCE is None:
       self.INSTANCE = wx.MiniFrame.__new__(self, *args, **kargs)
    return self.INSTANCE

  def Destroy(self):
    #----------------------------------------------------------------------------
    """Destroy the instance"""
    self.__class__.INSTANCE = None
    wx.MiniFrame.Destroy(self)

  def OnClose(self, evt):
    #----------------------------------------------------------------------------
    """Cleanup settings on close"""
    PickerFrame.INSTANCE = None
    evt.Skip()


#-----------------------------------------------------------------------------#
ID_SOMETHING = wx.NewId()

class PickerPanel(wx.PyPanel):
  """Creates the calculators interface
  @todo: Everything!
  """
  def __init__(self, parent, id_):
    """Initialiases the calculators main interface"""
    wx.PyPanel.__init__(self, parent, id_)
    self.col = wx.Color(255,255,0)
    self._layout()

  #------------------------------------------------------------------------
  def _layout(self):
    """ Layout """
    self.pnl1 = wx.Panel(self)
    self.pnl2 = wx.Panel(self)
    self.pnl3 = wx.Panel(self)

    colorBox1 = self.showPreview(self.pnl1)
    colorBox2 = self.showColor(self.pnl2)
    colorBox3 = self.ColorList(self.pnl3)

    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(self.pnl1, 0, wx.ALL|wx.EXPAND, border = 5)
    sizer.Add(self.pnl2, 0, wx.ALL|wx.EXPAND, border = 5)
    sizer.Add(self.pnl3, 0, wx.ALL|wx.EXPAND, border = 5)
    self.SetSizer(sizer)
    self.SetInitialSize()

    self.timer = wx.Timer(self)
    self.timer.Start(60)
    self.Bind(wx.EVT_TIMER, self.onPaint, self.timer)

  #------------------------------------------------------------------------
  def ColorList(self, pnl):
    sb = wx.StaticBox(pnl, label=" Color List ")

    panel = wx.Panel(pnl, size=(140,100))
    panel.SetInitialSize()
    
    self.index = 0
    self.list_ctrl = wx.ListCtrl(panel, size=(140,100), style=wx.LC_REPORT|wx.LC_NO_HEADER)
    self.list_ctrl.InsertColumn(0, '')

    self.list_ctrl.Bind(wx.EVT_KEY_DOWN, self.listKeyEvent)
    self.list_ctrl.SetFocus()

    sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
    sizer.Add(panel, 0, wx.EXPAND|wx.ALL|wx.SIMPLE_BORDER, border = 1)
    pnl.SetSizer(sizer)

  #------------------------------------------------------------------------
  def showColor(self, pnl):
    sb = wx.StaticBox(pnl, label=" Color ")

    panel = wx.Panel(pnl, size=(140,100))
    panel.SetInitialSize()

    sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
    sizer.Add(panel, 0, wx.EXPAND|wx.ALL|wx.SIMPLE_BORDER, border = 1)
    pnl.SetSizer(sizer)
    colorImage = wx.EmptyBitmapRGBA(140, 40, 255,255,255, alpha=0)
    self.colorMap = wx.StaticBitmap(panel, -1, bitmap=colorImage)
    self.colorPos = wx.StaticText(panel, -1, 'X: 0, Y: 0', pos=(0,65))
    self.colorData = wx.StaticText(panel, -1, 'RGB: 0, 0, 0', pos=(0,45))
    self.colorHint = wx.StaticText(panel, -1, 'Grab with Ctrl+G', pos=(0,85))
    self.cpan = panel

  #------------------------------------------------------------------------
  def showPreview(self, pnl):
    sb = wx.StaticBox(pnl, label=" Preview ")

    panel = wx.Panel(pnl, size=(100,100))
    panel.SetInitialSize()

    sizer = wx.StaticBoxSizer(sb, wx.VERTICAL)
    sizer.Add(panel, 0, wx.EXPAND|wx.ALL|wx.SIMPLE_BORDER, border = 1)
    pnl.SetSizer(sizer)

    screenImage = wx.EmptyBitmapRGBA(100, 40, 255,255,255, alpha=0)
    self.screenMap = wx.StaticBitmap(panel, bitmap=screenImage)
    
    self.span = panel


  """ EVENTS BELLOW """
  #----------------------------------------------------------------------------
  def onPaint(self, evt):  
    r,g,b = self.getHoverColor()  
    pil_im = Image.new('RGB', (140,40), (r,g,b))

    image = wx.EmptyImage(pil_im.size[0], pil_im.size[1])
    image.SetData(pil_im.tostring())

    colorImage = wx.BitmapFromImage(image)
    self.colorMap.SetBitmap(bitmap=colorImage)
    wx.Yield()

    self.onPaintScreen(evt)

  def onPaintScreen(self, evt):  
    pil_im = self.getHoverScreen()
    pil_im = pil_im.resize((100,100), Image.NEAREST)

    image = wx.EmptyImage(pil_im.size[0], pil_im.size[1])
    image.SetData(pil_im.tostring())

    partImage = wx.BitmapFromImage(image)
    self.screenMap.SetBitmap(bitmap=partImage)
    wx.Yield()

  def getHoverColor(self):
    x,y = mouse.position()
    r,g,b = get_pixel_colour(x,y)
    self.colorData.SetLabel('RGB: %d, %d, %d' % (r,g,b))
    self.colorPos.SetLabel('X: %d, Y: %d' % (x,y))
    return r,g,b

  def getHoverScreen(self):
    x,y = mouse.position()
    img = grabScreen(x-10,y-10,x+10,y+10)
    draw = ImageDraw.Draw(img)
    draw.line(((20, 10) + (0,10)), fill=0)
    draw.line(((10, 20) + (10,0)), fill=0)
    del draw
    return img

  #----------------------------------------------------------------------
  def listKeyEvent(self, event):
    key = event.GetKeyCode()
    if key == ord('G') and event.ControlDown():
      x,y = mouse.position()
      r,g,b = get_pixel_colour(x,y)
      line = "RGB: %d, %d, %d" % (r, g, b)

      i = self.index
      ctrl = self.list_ctrl
      ctrl.InsertStringItem(i, line)
      ctrl.SetItemBackgroundColour(i, wx.Color(r, g, b))   
      ctrl.SetColumnWidth(i, 200)
      ctrl.Focus(i)

      self.index += 1

    elif key == ord('C') and event.ControlDown():
      item = self.list_ctrl.GetFocusedItem()
      text = self.list_ctrl.GetItemText(item)[5:]
      dataObj = wx.TextDataObject()
      dataObj.SetText(text)
      if wx.TheClipboard.Open():
        wx.TheClipboard.SetData(dataObj)
        wx.TheClipboard.Close()

    else:
      event.Skip()

#-----------------------------------------------------------------------------#
# Test
if __name__ == '__main__':
    APP = wx.App(False)
    PICKER = PickerFrame(None, ("Colorpicker"))
    PICKER.Show(True)
    APP.MainLoop()