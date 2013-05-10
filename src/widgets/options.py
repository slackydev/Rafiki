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

 --- Options/settings for the GUI ---                                            
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
import wx
import os, sys
import ConfigParser

if __name__ == '__main__':
  appdata = os.sep.join(sys.path[0].split(os.sep)[:-2]) + '/appdata/'
else:
  appdata = 'appdata/'

ID_OPT = wx.NewId()
CFG_FILE = appdata + "settings.conf"

def ShowOptions(parent):
  """Shows the calculator"""
  if parent != None:
    if OptionFrame.INSTANCE is None:
      OPTION = OptionFrame(parent, ("Rafiki - Options"))
      OPTION.Show(True)
    else:
      OptionFrame.INSTANCE.Destroy()
      OptionFrame.INSTANCE = None

#-----------------------------------------------------------------------------#
class OptionFrame(wx.Dialog):
  INSTANCE = None
  def __init__(self, parent, title):
    style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
    wx.Dialog.__init__(self, parent, wx.ID_ANY, title, style=style)

    # Attributes
    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(OptionPanel(self, ID_OPT), -1, wx.ALL|wx.EXPAND, border=3)
    self.SetSizer(sizer)
    self.SetInitialSize()
    if parent:
        self.CentreOnParent(wx.BOTH)
    self.SetMinSize((200,250))

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
    OptionFrame.INSTANCE = None
    evt.Skip()

#-===========================================================================-#
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| Notebook/Tab class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class OptionPanel(wx.Notebook):
  #----------------------------------------------------------------------
  """Creates the windows (tabs)
  @todo: Remove placeholders and think of more options
  """
  def __init__(self, parent, id_):
    wx.Notebook.__init__(self, parent, id_, style=wx.BK_TOP)
    self.AddPage(TAB_Interpreter(self), "Interpreter")
    self.AddPage(TAB_Visual(self),      "View ")
    self.AddPage(TAB_Editor(self),      "Editor")
    self.AddPage(TAB_Interpreter(self), "Place Holder")
    self.AddPage(TAB_Interpreter(self), "Place Holder")

    self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
    self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging)

  def onPageChanged(self, event):
    event.Skip()

  def onPageChanging(self, event):
    event.Skip()

#-===========================================================================-#
class TAB_Interpreter(wx.PyPanel):
  #--------------------------------------------------------------------------
  """Creates the "Interpreter" option menu
  @todo: Prettify
  """
  def __init__(self, parent):
    """ Initialiases the interface """
    wx.PyPanel.__init__(self, parent, id=-1)
    self.cfg = RConfig()

    self._layout()
    self.SetInitialSize()
    # Event Handlers
    self.cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
    self.save.Bind(wx.EVT_BUTTON, self.OnSave)
    

  def _layout(self):
    #--------------------------------------------------------------------------
    path_label = wx.StaticText(self, label='Interpreter path:')
    self.path = wx.TextCtrl(self)
    self.path.SetValue( self.cfg.getValue('INTERPRETER', 'path') )

    hbox1 = wx.BoxSizer(wx.HORIZONTAL)
    hbox1.Add(path_label, flag=wx.ALL, border=3)
    hbox1.Add(self.path, proportion=1)

    #---------
    self.cb1 = wx.CheckBox(self, label='Use default interpreter \t (default: yes)')
    self.cb2 = wx.CheckBox(self, label='Unbuffered \t\t\t (default: yes)')
    self.cb3 = wx.CheckBox(self, label='Hide warnings \t\t\t (default: yes)')

    self.cb1.SetValue( self.cfg.getValue('INTERPRETER', 'default', bool) ) 
    self.cb2.SetValue( self.cfg.getValue('INTERPRETER', 'unbuffered', bool) ) 
    self.cb3.SetValue( self.cfg.getValue('INTERPRETER', 'hidewarn', bool) ) 

    hbox2 = wx.BoxSizer(wx.VERTICAL)
    hbox2.Add(self.cb1, border=10)
    hbox2.Add(self.cb2, border=10)
    hbox2.Add(self.cb3, border=10)

    #---------
    arg_about = 'Other startup arguments for python (separate with comma):'
    arg_text = wx.StaticText(self, label=arg_about)
    self.arguments = wx.TextCtrl(self, style=wx.TE_MULTILINE)
    self.arguments.SetValue( self.cfg.getValue('INTERPRETER', 'other') ) 

    hbox3 = wx.BoxSizer(wx.VERTICAL)
    hbox3.Add(arg_text)
    hbox3.Add(self.arguments, proportion=1, flag=wx.EXPAND)

    #---------
    self.save = wx.Button(self, label='Save', size=(70, 30))
    self.cancel = wx.Button(self, label='Cancel', size=(70, 30))

    hbox4 = wx.BoxSizer(wx.HORIZONTAL)
    hbox4.Add(self.save)
    hbox4.Add(self.cancel, flag=wx.LEFT|wx.BOTTOM, border=5)

    #----------------------------------------------------------------#
    mainbox = wx.BoxSizer(wx.VERTICAL)
    mainbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=6)
    mainbox.Add((-1, 10))
    mainbox.Add(hbox2, flag=wx.LEFT, border=6)
    mainbox.Add((-1, 10))
    mainbox.Add(hbox3, proportion=1, flag=wx.EXPAND|wx.ALL, border=6)
    mainbox.Add((-1, 25))
    mainbox.Add(hbox4, flag=wx.ALIGN_RIGHT|wx.ALL, border=6)

    self.SetSizer(mainbox)

  def OnSave(self, evt):
    #--------------------------------------------------------------------------
    """ Save settings """
    self.cfg.setValue('INTERPRETER', 'path',   self.path.GetValue())
    self.cfg.setValue('INTERPRETER', 'default',     self.cb1.GetValue())
    self.cfg.setValue('INTERPRETER', 'unbuffered',  self.cb2.GetValue())
    self.cfg.setValue('INTERPRETER', 'hidewarn',    self.cb3.GetValue())
    self.cfg.setValue('INTERPRETER', 'other',       self.arguments.GetValue())
    evt.Skip()

  def OnCancel(self, evt):
    #--------------------------------------------------------------------------
    """ Save settings """
    evt.Skip()


#-===========================================================================-#
class TAB_Visual(wx.PyPanel):
  #--------------------------------------------------------------------------
  """Creates the "Visual" option menu
  @todo: Prettify
  """
  def __init__(self, parent):
    """ Initialiases the interface """
    wx.PyPanel.__init__(self, parent, id=-1)
    self.cfg = RConfig()

    self._layout()
    self.SetInitialSize()

    # Event Handlers
    self.cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
    self.save.Bind(wx.EVT_BUTTON, self.OnSave)
    

  def _layout(self):
    #---------
    self.cb1 = wx.CheckBox(self, label='View linenumber \t\t\t (default: yes)')
    self.cb2 = wx.CheckBox(self, label='Wrap text \t\t\t\t (default: no)')
    self.cb3 = wx.CheckBox(self, label='Highlight matching braces \t (default: yes)')
    self.cb4 = wx.CheckBox(self, label='View indentation guides \t\t (default: yes)')
    self.cb5 = wx.CheckBox(self, label='Use syntax-highliting \t\t (-not implemented-)')

    self.cb1.SetValue( self.cfg.getValue('VISUAL', 'linenumber', bool) )
    self.cb2.SetValue( self.cfg.getValue('VISUAL', 'wraptext', bool) )
    self.cb3.SetValue( self.cfg.getValue('VISUAL', 'highlightbraces', bool) )
    self.cb4.SetValue( self.cfg.getValue('VISUAL', 'indentguides', bool) )
    self.cb5.SetValue( self.cfg.getValue('VISUAL', 'syntaxhighlighing', bool) )

    hbox1 = wx.BoxSizer(wx.VERTICAL)
    hbox1.Add(self.cb1, flag=wx.ALL, border=3)
    hbox1.Add(self.cb2, flag=wx.ALL, border=3)
    hbox1.Add(self.cb3, flag=wx.ALL, border=3)
    hbox1.Add(self.cb4, flag=wx.ALL, border=3)
    hbox1.Add(self.cb5, flag=wx.ALL, border=3)

    #---------
    self.save = wx.Button(self, label='Save', size=(70, 30))
    self.cancel = wx.Button(self, label='Cancel', size=(70, 30))

    hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    hbox2.Add(self.save)
    hbox2.Add(self.cancel, flag=wx.LEFT|wx.BOTTOM, border=5)

    #----------------------------------------------------------------#
    mainbox = wx.BoxSizer(wx.VERTICAL)
    mainbox.Add(hbox1, flag=wx.LEFT|wx.TOP|wx.EXPAND|wx.ALL, border=6)
    mainbox.Add((-1, 40))
    mainbox.Add(hbox2, flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.ALL, border=6)

    self.SetSizer(mainbox)

  def OnSave(self, evt):
    #--------------------------------------------------------------------------
    """ Save settings """
    self.cfg.setValue('VISUAL', 'linenumber',         self.cb1.GetValue())
    self.cfg.setValue('VISUAL', 'wraptext',           self.cb2.GetValue())
    self.cfg.setValue('VISUAL', 'highlightbraces',    self.cb3.GetValue())
    self.cfg.setValue('VISUAL', 'indentguides',       self.cb4.GetValue())
    self.cfg.setValue('VISUAL', 'syntaxhighlighing',  self.cb5.GetValue())
    evt.Skip()

  def OnCancel(self, evt):
    #--------------------------------------------------------------------------
    """ Save settings """
    evt.Skip()

#-===========================================================================-#
class TAB_Editor(wx.PyPanel):
  #--------------------------------------------------------------------------
  """Creates the "Editor" option menu
  @todo: Prettify
  """
  def __init__(self, parent):
    """ Initialiases the interface """
    wx.PyPanel.__init__(self, parent, id=-1)
    self.cfg = RConfig()

    self._layout()
    self.SetInitialSize()

    # Event Handlers
    self.cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
    self.save.Bind(wx.EVT_BUTTON, self.OnSave)
    

  def _layout(self):
    HEADER = wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD) 

    #---------
    tabs_size = ['  %s  ' %x for x in range(9)]
    tabs_text = wx.StaticText(self, -1, "Indentation size:", (15, 20))
    self.tabs_choice = wx.Choice(self, -1, choices=tabs_size, size=(100, 25))
    self.tabs_choice.SetSelection(( self.cfg.getValue('EDITOR', 'indentsize', int) ))

    hbox1 = wx.BoxSizer(wx.HORIZONTAL)
    hbox1.Add(tabs_text, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=4)
    hbox1.Add(self.tabs_choice, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=0)

    #---------
    self.use_space = wx.CheckBox(self, label='Indent with &Space instead of &Tab (default: yes)')
    self.use_space.SetValue( self.cfg.getValue('EDITOR', 'usespace', bool) )
    hbox2 = wx.BoxSizer(wx.VERTICAL)
    hbox2.Add(self.use_space, flag=wx.ALL, border=0)


    #---------
    self.quick_indent = wx.CheckBox(self, label='Use auto indentation (default: yes)')
    self.quick_indent.SetValue( self.cfg.getValue('EDITOR', 'autoindent', bool) )
    hbox3 = wx.BoxSizer(wx.VERTICAL)
    hbox3.Add(self.quick_indent, flag=wx.ALL, border=0)

    #---------
    self.save = wx.Button(self, label='Save', size=(70, 30))
    self.cancel = wx.Button(self, label='Cancel', size=(70, 30))

    hbox4 = wx.BoxSizer(wx.HORIZONTAL)
    hbox4.Add(self.save)
    hbox4.Add(self.cancel, flag=wx.LEFT|wx.BOTTOM, border=5)

    #----------------------------------------------------------------#
    header_indent = wx.StaticText(self, label='Indentation')
    header_autoindent = wx.StaticText(self, label='Auto Indentation')
    header_indent.SetFont(HEADER)
    header_autoindent.SetFont(HEADER)

    mainbox = wx.BoxSizer(wx.VERTICAL)
    mainbox.Add((-1, 10))
    mainbox.Add(header_indent, flag=wx.ALL, border=3)
    mainbox.Add(hbox1, flag=wx.LEFT, border=6)

    mainbox.Add((-1, 0))
    mainbox.Add(hbox2, flag=wx.LEFT, border=6)

    mainbox.Add((-1, 10))
    mainbox.Add(header_autoindent, flag=wx.ALL, border=3)
    mainbox.Add(hbox3, flag=wx.LEFT, border=6)

    mainbox.Add((-1, 40))
    mainbox.Add(hbox4, flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.ALL, border=6)

    self.SetSizer(mainbox)

  def OnSave(self, evt):
    #--------------------------------------------------------------------------
    """ Save settings """

    self.cfg.setValue('EDITOR', 'indentsize', self.tabs_choice.GetSelection())
    self.cfg.setValue('EDITOR', 'usespace',   self.use_space.GetValue())
    self.cfg.setValue('EDITOR', 'autoindent', self.quick_indent.GetValue())
    evt.Skip()

  def OnCancel(self, evt):
    #--------------------------------------------------------------------------
    """ Save settings """

    evt.Skip()
  

#-===========================================================================-#
class RConfig(object):
  #----------------------------------------------------------------------------
  """Configuration file - read/write
  @todo: Most all
  """
  def __init__(self):
    #For simple reading
    self.parser = ConfigParser.ConfigParser()
    self.parser.read(CFG_FILE)

  def getValue(self, sect, index, mode=str):
    if mode==str:
      return self.parser.get(sect, index)
    elif mode==bool:
      return self.parser.getboolean(sect, index)
    elif mode==int:
      return self.parser.getint(sect, index)
    elif mode==float:
      return self.parser.getfloat(sect, index)

  def setValue(self, sect, index, value):
    cfgfile = open(CFG_FILE, 'w')
    self.parser.set(sect, index, value)
    self.parser.write(cfgfile)
    cfgfile.close()

#-===========================================================================-#
# Test
if __name__ == '__main__':
    APP = wx.App(False)
    OPTION = OptionFrame(None, ("Options"))
    OPTION.Show(True)
    APP.MainLoop()