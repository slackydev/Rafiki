#!/usr/bin/env python
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

 --- Graphical user interface for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
import wx
import wx.stc as stc
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub as Publisher
import wx.html
from wx.py.shell import Shell
import webbrowser
import keyword
import sys, os
import glob
import time
import subprocess 
import platform
import re, string

from random import randint
from threading import Thread

''' Rafiki widgets '''
sys.path.insert(1, os.path.join(sys.path[0], 'src/'))

from src.widgets import calc, colorpicker, options
from src.widgets import DirTreeCtrl as DTC

if platform.system() == 'Windows':
  from src.pywin_api import *
  import _subprocess

if platform.system() == 'Linux':
  pass

ID_START   = 50
ID_STOP    = 51
ID_FIND    = 52
ID_REPLACE = 53
ID_GOTO    = 54
ID_CLEAR   = 55

ID_NEW    = 102
ID_NEWTAB = 103
ID_OPEN   = 104
ID_RECENT = 105
ID_SAVE   = 106
ID_SAVEAS = 107

ID_EXIT = 200

ID_PICKCOLOR = 300
ID_PICKBMP   = 301
ID_PRTSCN    = 302
ID_BMPToStr  = 303
ID_StrToBMP  = 304
ID_DTMEditor = 305
ID_WINDOW    = 306
ID_NUMBERS   = 307

ID_SYNTAXCTRL = 400
ID_OPTIONS    = 401

ID_WEB    = 500
ID_ABOUT  = 501

#Set current working dir here..
os.chdir(sys.path[0])
ICONS = 'src/icons/'

#Do not open binary files!
BADEXT = DTC.audio + DTC.video + DTC.image + DTC.binary + DTC.compr

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| Initalize rafiki
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class App(wx.App):
  #----------------------------------------------------------------------
  def OnInit(self):
    frame = RafikiFrame('Rafiki Pre-Alpha')
    self.SetTopWindow(frame)
    return True


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| The main frame that connects everything
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class RafikiFrame(wx.Frame):
  #----------------------------------------------------------------------
  def __init__(self, name):
    wx.Frame.__init__(self, None, -1, title=name)
    # Global variables
    self.title = name
    self.files = {}
    self.running = False
    self.SE = ScriptEngine(self)

    # Layout part 1...
    FileMenu(self)
    Toolbar(self)

    self.SetMinSize((400,400))
    self._layout()
    self.Centre()
    self.Show()
    self.SetSize((900, 800))

    # CONNECT EVENTS
    Publisher.subscribe(self.scriptMsg, "update")
    self.tc.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onActivateFile)

  def _layout(self):
    """ Setup the layout - well... part 2 """
    window = wx.SplitterWindow(self, -1)
    self.panel1 = wx.Panel(window, -1)
    self.panel2 = wx.Panel(window, -1)
    self.panel1.SetBackgroundColour(wx.Colour(205,205,205))

    # RIGHT SIDE PANEL / self.panel1
    self.stxt = wx.StaticText(self.panel1, -1, label=" File browser")
    self.stxt.SetForegroundColour((35,35,35))

    self.tc = DTC.DirTreeCtrl(self)
    self.cpath = os.path.dirname(os.path.realpath(__file__))
    self.tc.SetRootDir(self.cpath)
    
    rpan = wx.BoxSizer(wx.VERTICAL)
    rpan.Add(self.stxt, 0, wx.EXPAND|wx.ALL, border = 2)
    rpan.Add(self.tc, 10, wx.EXPAND|wx.ALL, border = 1)
    self.panel1.SetSizer(rpan)

    # LEFT SIDE PANEL / self.panel2
    hsplit = wx.SplitterWindow(self.panel2)
    self.ntb = Notebook(hsplit, self)
    self.debug = DebugControl(hsplit, self)

    hsplit.SetSashGravity(0.8)
    hsplit.SplitHorizontally(self.ntb, self.debug)
    hsplit.SetMinimumPaneSize(80)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(hsplit, 1, wx.EXPAND|wx.ALL, border = 2)
    self.panel2.SetSizer(sizer)

    # ADD PANELS
    window.SetSashGravity(0.08)
    window.SplitVertically(self.panel1, self.panel2)
    window.SetMinimumPaneSize(150)

    self.SetSizer(wx.BoxSizer(wx.HORIZONTAL))
    self.GetSizer().Add(window, 1, wx.EXPAND)

    self.sb = self.CreateStatusBar(2)
    self.sb.SetStatusWidths([-1, 150])


    ico = wx.Icon(ICONS+'rafiki.ico', wx.BITMAP_TYPE_ICO)
    self.SetIcon(ico)
    self.Layout()


  ''' General environment features '''
  #-----------------------------------------------------------
  def onExit(self, event):
    """ Exit rafiki """
    dlg = wx.MessageDialog(self,
            "Are you sure you want to close Rafiki?",
            "Confirm Exit", wx.YES|wx.NO|wx.ICON_QUESTION)
    result = dlg.ShowModal()
    dlg.Destroy()
  
    if result == wx.ID_YES:
      self.Destroy()

  def onOpen(self, event):
    """Open file from dir"""
    dir = os.path.dirname(os.path.realpath(__file__))
    dlg = wx.FileDialog(self, "Choose a file...", dir, "", "*.*", wx.OPEN)
    if dlg.ShowModal() == wx.ID_OK:
      filename = dlg.GetFilename()
      dirname = dlg.GetDirectory()

      data = os.path.splitext(filename)

      # Is it a binary file?
      if data[1] in BADEXT: return None

      filehandle=open(os.path.join(dirname, filename),'rb')
      self.onNewDoc(0)
      page = self.ntb.GetCurrentPage()
      page.text.SetText(filehandle.read().encode("utf8"))
      filehandle.close()

      page_id = self.ntb.GetSelection()
      self.ntb.SetPageText(page_id, filename)

      titledir = dirname
      if len(dirname)>30: #Hint: os.sep
        titledir = ".." + titledir[-20:] + "/"

      self.files[page_id] = (dirname, filename) 
      self.SetTitle(self.title + " | "+ titledir + filename)

    dlg.Destroy()

  def onActivateFile(self, evt):
    """ Open a file doubbleclicked in the treectrl """
    ID = evt.GetItem()
    filename = self.tc.GetItemText(ID)
    if filename == self.cpath.split(os.sep)[-1]:
      return None

    
    dirname = self.getItemPath(ID)[:-len(filename)]
    data = os.path.splitext(filename)

    
    if data[1] not in BADEXT:
      filehandle=open(os.path.join(dirname, filename),'rb')
      self.onNewDoc(0)
      page = self.ntb.GetCurrentPage()
      page.text.SetText(filehandle.read().encode("utf8"))
      filehandle.close()

      page_id = self.ntb.GetSelection()
      self.ntb.SetPageText(page_id, filename)

      titledir = dirname
      if len(dirname)>30: #Hint: os.sep
        titledir = ".." + titledir[-20:]

      self.files[page_id] = (dirname, filename) 
      self.SetTitle(self.title + " | "+ titledir + filename)
    
  def onNewDoc(self, event):
    """Add tab, and select it"""
    self.ntb.addNewTab(event)
    self.ntb.SetSelection(self.ntb.GetPageCount()-1)

  def onNewTab(self, event):
    """Add tab"""
    self.ntb.addNewTab(event)

  def onSave(self, event):
    """ Quick save file current dir
    """
    page_id = self.ntb.GetSelection()
    filedata = self.files.get(page_id)
    if filedata:
      try:
        filehandle=open(os.path.join(filedata[0], filedata[1]), 'wb')
        page = self.ntb.GetCurrentPage()
        itcontains = page.text.GetText().encode("utf8")
        filehandle.write(itcontains)
        filehandle.close()
        self.writeLn("Saved file: %s" % filedata[1])
      except Exception as exc:
        self.writeLn("Error occured when trying to save file! %s" % exc)
    else:
      self.onSaveAs(event)

  def onSaveAs(self, event):
    """ Save file to given folder 
    """
    dirname = os.path.dirname(os.path.realpath(__file__))
    params = "Python (*.py)|*.py|"
    params += "Plain text (*.txt)|*.txt|"
    params += "Other (*.*)|*.*"
    dlg = wx.FileDialog(self, "Save project...", dirname, "", params, 
                        wx.SAVE|wx.OVERWRITE_PROMPT)

    if dlg.ShowModal() == wx.ID_OK:
      page_id = self.ntb.GetSelection()
      page = self.ntb.GetCurrentPage()
      itcontains = page.text.GetText().encode("utf8")

      filename = dlg.GetFilename()
      dirname = dlg.GetDirectory()

      filehandle=open(os.path.join(dirname, filename), 'wb')
      filehandle.write(itcontains)
      filehandle.close()
            
      titledir = dirname
      if len(dirname)>30: #Hint: os.sep
        titledir = dirname.split(os.sep)[-1]
        titledir = "~/" + titledir[-20:] + "/"

      self.writeLn("Saved file: %s" % filename)
      self.files[page_id] = (dirname, filename) 
      self.SetTitle(self.title + " | "+ titledir + filename)
      self.ntb.SetPageText(page_id, filename)

    dlg.Destroy()

  def onAbout(self, event):
    """ None """
    AboutFrame().Show()

  def clearDebug(self, event):
    """ Clear out the debug """
    dbg = self.debug.GetPage(0)
    dbg.Clear()

  def writeLn(self, text, style=None):
    """ Print text to the debug """
    dbg = self.debug.GetPage(0)
    if text.endswith("\n"):
      dbg.Insert(text)
    else:
      dbg.InsertLn(text)

  def getItemPath(self, itemId):
    """ Get and return the path of the given item id
        @param itemId: TreeItemId
    """

    root = self.tc.GetRootItem()
    start = itemId
    atoms = [itemId]

    while self.tc.GetItemParent(start) != root:
        atoms.append(self.tc.GetItemParent(start))
        start = atoms[-1]

    atoms.reverse()
    path = list()
    for atom in atoms:
        path.append(self.tc.GetItemText(atom))

    if wx.Platform == '__WXGTK__':
      if path[0].lower() == 'home directory':
        path[0] = wx.GetHomeDir()
      elif path[0].lower() == 'desktop':
        path.insert(0, wx.GetHomeDir())
      else:
        pass

    return os.sep.join(path)

  def onFind(self, event):
    """ @todo Create a dialog! 
    """
    page = self.ntb.GetCurrentPage()
    pg = page.text
    length = pg.GetTextLength()
    currpos = pg.GetCurrentPos()
    word = 'find'
    result = pg.FindText(currpos, length, word, 0);
    if result == -1:
      result = pg.FindText(0, length, word, 0);
    pg.GotoPos(result + len(word))

  def onFindAndReplace(self):
    pass


  ''' Scriptengine related function calls '''
  #-----------------------------------------------------------
  def runScript(self, event):
    if self.running == False:
      page = self.ntb.GetCurrentPage()
      script = page.text.GetText()
      self.SE.runscript(script=script, wnd=[0,0,1500,900])
      self.running = True

  def killScript(self, event):
    if self.running == True:
      self.SE.killscript()

  def scriptMsg(self, event):
    data = event.data
    # if it's a string then post it
    dbg = self.debug.GetPage(0)
    if isinstance(data, str):
      if data.endswith("\n"):
        dbg.Insert(data)
      else:
        dbg.InsertLn(data)

    ''' if it's a boolean then we know the thread is over '''
    if isinstance(data, bool):
      self.running = False

  #-----------------------------------------------------------
  ''' Rafiki tools and special features '''
  def colorPicker(self,event):
    inst = wx.GetApp().TopWindow
    colorpicker.ShowPicker(inst)

  def bmpPicker(self,event):
    AboutFrame().Show()

  def bmp2str(self,event):
    AboutFrame().Show()

  def str2bmp(self,event):
    AboutFrame().Show()

  def dtmEditor(self,event):
    AboutFrame().Show()

  def calculator(self,event):
    inst = wx.GetApp().TopWindow
    calc.ShowCalculator(inst)

  def syntaxEditor(self,event):
    AboutFrame().Show()

  def optionMenu(self,event):
    inst = wx.GetApp().TopWindow
    options.ShowOptions(inst)

  def windowArea(self,event):
    AboutFrame().Show()



'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| A simple debugbox
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class DebugPanel(wx.Panel):
  #----------------------------------------------------------------------
  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
    stylesheet = wx.TE_MULTILINE|wx.TE_RICH2|wx.HSCROLL|wx.TE_READONLY
    self.dbg = wx.TextCtrl(self, wx.ID_ANY, style=stylesheet)

    font = 'Liberation Mono' if os.name=='posix' else 'Courier New' 
    fontData = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False, font)
    self.dbg.SetFont(fontData)

    dbgctrl = wx.BoxSizer(wx.VERTICAL)
    dbgctrl.Add(self.dbg, -1, wx.EXPAND)
    self.SetSizer(dbgctrl)

  def Insert(self, text):
      self.dbg.WriteText(text)

  def InsertLn(self, text):
      self.dbg.WriteText(text+'\n')

  def Clear(self):
    self.dbg.SetValue("")


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| Python shell tool
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class PyShell(wx.Panel):
  #----------------------------------------------------------------------
  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
    sh = wx.BoxSizer(wx.VERTICAL)
    sh.Add(Shell(self, -1), -1, wx.ALL|wx.EXPAND, border = 0)
    self.SetSizer(sh)


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| Notebook/Tab class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class DebugControl(wx.Notebook):
  #----------------------------------------------------------------------
  def __init__(self, parent, rafiki):
    wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_TOP)
    self.AddPage(DebugPanel(self), "Debug panel")
    self.AddPage(PyShell(self), "Python shell")


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| This is the skeleton for each tab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class TabPanel(wx.Panel):
  #----------------------------------------------------------------------
  '''@todo: Autoupdate when settings are changed
  '''
  def __init__(self, parent):
    wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)

    #----- PERSONAL CONFIGURATION
    config = options.RConfig()
    indent_size      = config.getValue('EDITOR', 'indentsize', int)
    use_space        = config.getValue('EDITOR', 'usespace', bool)
    auto_indent      = config.getValue('EDITOR', 'autoindent', bool)
    indent_guides    = config.getValue('VISUAL', 'indentguides', bool)
    highlight_braces = config.getValue('VISUAL', 'highlightbraces', bool)
    wrap_text        = config.getValue('VISUAL', 'wraptext', bool)


    #----- EDITOR
    textctrl = wx.BoxSizer(wx.VERTICAL)
    text = stc.StyledTextCtrl(self)
    self.text = text  #make it global

    text.SetWindowStyle(text.GetWindowStyle() | wx.DOUBLE_BORDER) #border style
    text.SetLayoutCache(stc.STC_CACHE_PAGE)
    text.SetTabWidth(indent_size)
    if use_space:
      text.SetUseTabs(False)

    text.SetIndentationGuides(indent_guides)

    #----- EDGES ACCORDING TO PEP-8
    text.SetEdgeColumn(79)
    text.SetEdgeMode(stc.STC_EDGE_LINE)
    text.SetProperty("fold", "1")
    text.SetProperty("tab.timmy.whinge.level", "1")


    #----- STYLECONTROL
    font = 'Liberation Mono' if os.name=='posix' else 'Courier New' 
    text.StyleSetSpec(stc.STC_STYLE_DEFAULT, "fore:#000000,size:10,face:%s" % font)
    text.StyleClearAll();
        
    text.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  'back:#C0C0C0')
    text.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, 'fore:#537553')

    if highlight_braces:
      text.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  'fore:#000080,underline')
      text.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    'fore:#FF2222,bold')

    text.SetLexer(stc.STC_LEX_PYTHON)
    kword  = '''and del from not while as elif global or with
                assert else if pass yield break except import print
                class exec in raise continue finally is return 
                def for lambda try len True False None'''
    text.SetKeyWords(0, kword)

    # Comments
    text.StyleSetSpec(stc.STC_P_COMMENTLINE,  'fore:#537553,back:#F0FFF0')
    text.StyleSetSpec(stc.STC_P_COMMENTBLOCK, 'fore:#537553,back:#F0FFF0')
    # Numbers
    text.StyleSetSpec(stc.STC_P_NUMBER, 'fore:#ff0000')
    # Strings and characters
    text.StyleSetSpec(stc.STC_P_STRING, 'fore:#e77800')
    text.StyleSetSpec(stc.STC_P_CHARACTER, 'fore:#e77800')
    # Keywords
    text.StyleSetSpec(stc.STC_P_WORD, 'fore:#000000,bold,italic')
    # Triple quotes
    text.StyleSetSpec(stc.STC_P_TRIPLE, 'fore:#800080,back:#FFFFEA')
    text.StyleSetSpec(stc.STC_P_TRIPLEDOUBLE, 'fore:#800080,back:#FFFFEA')
    # Class names
    text.StyleSetSpec(stc.STC_P_CLASSNAME, 'fore:#000000')
    # Function names
    text.StyleSetSpec(stc.STC_P_DEFNAME, 'fore:#000000')
    # Operators
    text.StyleSetSpec(stc.STC_P_OPERATOR, 'fore:#000080')    
    # Set linenumber style
    text.StyleSetSpec(stc.STC_STYLE_LINENUMBER, "back:#C9D7E7")
    # Selection background
    text.SetSelBackground(1, '#89c3f4')
    # Current line highlighting

    text.SetCaretLineBackground(wx.Colour(235,235,235))
    text.SetCaretLineVisible(True)

    if wrap_text:
      text.SetWrapMode(stc.STC_WRAP_WORD)
    else:
      text.SetWrapMode(stc.STC_WRAP_NONE)

    #----- LEFT MARGIN (controller)
    text.SetMarginLeft(3)
    text.SetMarginSensitive(2, True)
    text.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
    text.SetMarginMask(2, stc.STC_MASK_FOLDERS)
    
    #----- FOLDING
    text.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,    stc.STC_MARK_BOXMINUS,          "white", "#808080")
    text.MarkerDefine(stc.STC_MARKNUM_FOLDER,        stc.STC_MARK_BOXPLUS,           "white", "#808080")
    text.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,     stc.STC_MARK_VLINE,             "white", "#808080")
    text.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,    stc.STC_MARK_LCORNER,           "white", "#808080")
    text.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,     stc.STC_MARK_BOXPLUSCONNECTED,  "white", "#808080")
    text.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID, stc.STC_MARK_BOXMINUSCONNECTED, "white", "#808080")
    text.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL, stc.STC_MARK_TCORNER,           "white", "#808080")

    #----- LEFT MARGIN (Linenuber and Folding)
    text.SetMarginWidth(2, 12)
    text.SetMarginWidth(1, text.TextWidth(stc.STC_STYLE_LINENUMBER, " "))
    text.SetMarginWidth(0, text.TextWidth(stc.STC_STYLE_LINENUMBER, "  "))
    text.SetText("\n\n")

    #----- EVENT BINDING
    text.Bind(stc.EVT_STC_CHANGE, self.onUpdate)
    text.Bind(stc.EVT_STC_UPDATEUI, self.onUpdateUI)
    text.Bind(stc.EVT_STC_MARGINCLICK, self.onMarginClick)
    text.Bind(wx.EVT_KEY_DOWN, self.onKeyPressed)

    # Finally.. Add it.
    textctrl.Add(self.text, -1, wx.EXPAND)
    self.SetSizer(textctrl)

  ''' When a change is found, this is called '''
  def onUpdate(self, evt):
    # Update margin linecount
    lines = self.text.GetLineCount()
    width = self.text.TextWidth(stc.STC_STYLE_LINENUMBER, str(lines) +" ")
    self.text.SetMarginWidth(0, width)

  def onKeyPressed(self, event):
    ''' @Todo: Autogenerate / grab function- and class-names
    '''
    key = event.GetKeyCode()

    if key == 32 and event.ControlDown():
      pos = self.text.GetCurrentPos()
      start = 0 if pos < 50 else 50
      word = re.split('[\W]+', self.text.GetText()[start:pos])[-1]
      if word=="": 
        return None
      steps = len(word)  

      kw = keyword.kwlist[:]
      #kw.append("someword")
      kw.sort()

      kw[:] = [x for x in kw if (word in x)]
      if not kw: return

      self.text.AutoCompSetIgnoreCase(True)
      self.text.AutoCompShow(steps, " ".join(kw))

    else:
      event.Skip()
  

  ''' When UI is updated, this is called '''
  def onUpdateUI(self, evt):
    # check for matching braces
    braceAtCaret = -1
    braceOpposite = -1
    charBefore = None
    caretPos = self.text.GetCurrentPos()

    if caretPos > 0:
      charBefore = self.text.GetCharAt(caretPos - 1)
      styleBefore = self.text.GetStyleAt(caretPos - 1)

    # check before
    if charBefore and chr(charBefore) in "[]{}()" and \
          styleBefore == stc.STC_P_OPERATOR:
      braceAtCaret = caretPos - 1

    # check after
    if braceAtCaret < 0:
      charAfter = self.text.GetCharAt(caretPos)
      styleAfter = self.text.GetStyleAt(caretPos)

      if charAfter and chr(charAfter) in "[]{}()" and \
            styleAfter == stc.STC_P_OPERATOR:
        braceAtCaret = caretPos

    if braceAtCaret >= 0:
      braceOpposite = self.text.BraceMatch(braceAtCaret)

    if braceAtCaret != -1  and braceOpposite == -1:
      self.text.BraceBadLight(braceAtCaret)
    else:
      self.text.BraceHighlight(braceAtCaret, braceOpposite)


  ''' When margin is clicked, this is called '''
  def onMarginClick(self, evt):
    # fold and unfold as needed
    if evt.GetMargin() == 2:
      if evt.GetShift() and evt.GetControl():
        self.FoldAll()
      else:
        lineClicked = self.text.LineFromPosition(evt.GetPosition())

        if self.text.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
          if evt.GetShift():
            self.text.SetFoldExpanded(lineClicked, True)
            self.Expand(lineClicked, True, True, 1)
          elif evt.GetControl():
            if self.text.GetFoldExpanded(lineClicked):
              self.text.SetFoldExpanded(lineClicked, False)
              self.Expand(lineClicked, False, True, 0)
            else:
              self.text.SetFoldExpanded(lineClicked, True)
              self.Expand(lineClicked, True, True, 100)
          else:
            self.text.ToggleFold(lineClicked)
  
  # Fold or unfold all
  def FoldAll(self):
    lineCount = self.text.GetLineCount()
    expanding = True

    # find out if we are folding or unfolding
    for lineNum in range(lineCount):
      if self.text.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
        expanding = not self.text.GetFoldExpanded(lineNum)
        break

    lineNum = 0
    while lineNum < lineCount:
      level = self.text.GetFoldLevel(lineNum)
      if level & stc.STC_FOLDLEVELHEADERFLAG and \
          (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

        if expanding:
          self.text.SetFoldExpanded(lineNum, True)
          lineNum = self.Expand(lineNum, True)
          lineNum = lineNum - 1
        else:
          lastChild = self.text.GetLastChild(lineNum, -1)
          self.text.SetFoldExpanded(lineNum, False)

          if lastChild > lineNum:
            self.text.HideLines(lineNum+1, lastChild)

      lineNum = lineNum + 1

  # Fold or unfold the selection
  def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
    lastChild = self.text.GetLastChild(line, level)
    line = line + 1

    while line <= lastChild:
      if force:
        if visLevels > 0:
          self.text.ShowLines(line, line)
        else:
          self.text.HideLines(line, line)
      else:
        if doExpand:
          self.text.ShowLines(line, line)

      if level == -1:
        level = self.text.GetFoldLevel(line)

      if level & stc.STC_FOLDLEVELHEADERFLAG:
        if force:
          if visLevels > 1:
            self.text.SetFoldExpanded(line, True)
          else:
            self.text.SetFoldExpanded(line, False)
          line = self.Expand(line, doExpand, force, visLevels-1)

        else:
          if doExpand and self.text.GetFoldExpanded(line):
            line = self.Expand(line, True, force, visLevels-1)
          else:
            line = self.Expand(line, False, force, visLevels-1)
      else:
        line = line + 1

    return line


'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| Notebook/Tab class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class Notebook(wx.Notebook):
  #----------------------------------------------------------------------
  def __init__(self, parent, rafiki):
    wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
    self.menuOptions()
    self.tab_id = -1;
    self.rafiki = rafiki
    self.AddPage(TabPanel(self), "New project")

    self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
    self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onPageChanging)

    wx.EVT_RIGHT_DOWN(self, self.onRightClick) 

  def menuOptions(self):
    self.menu = wx.Menu()
    self.menu.Append(997, 'Close tab')
    self.menu.Append(998, 'Rename project')
    self.menu.Append(999, 'New project')

    wx.EVT_MENU(self, 997, self.closeTab)
    wx.EVT_MENU(self, 998, self.renameTab)
    wx.EVT_MENU(self, 999, self.addNewTab)

  def addNewTab(self, event):
    self.AddPage(TabPanel(self), "New project: %d" % self.GetPageCount())

  def onRightClick(self, event):
    position = event.GetPosition()
    index, type = self.HitTest(position)
    if index > -1:
      page = self.GetPage(index) 
      self.tab_id = index
      self.PopupMenu(self.menu, position)

  def renameTab(self, event):
    dia = RenameTabDialog(self)
    dia.ShowModal()
    dia.Destroy()
    page_id = self.GetSelection()
    newTitle = self.rafiki.title + " | "+ self.GetPageText(page_id)
    self.rafiki.SetTitle(newTitle)

  def closeTab(self, event):
    rafiki = self.rafiki
    if self.tab_id > -1:
      self.DeletePage(self.tab_id)
      pagedir = rafiki.files.get(self.tab_id)
      if pagedir: rafiki.files.pop(self.tab_id)
      self.tab_id = -1

  def onPageChanged(self, event):
    page_id = self.GetSelection()
    data = self.rafiki.files.get(page_id)
    newTitle = self.rafiki.title + " | "+ self.GetPageText(page_id)
    if data:
      filename = data[1]
      dirname = data[0]
      if len(dirname)>30: #Hint: os.sep
        titledir = dirname.split(os.sep)[-1]
        titledir = "~/" + titledir[-20:] + os.sep
      else:
        titledir = dirname

      newTitle = self.rafiki.title + " | "+ titledir + filename
    self.rafiki.SetTitle(newTitle)
    event.Skip()

  def onPageChanging(self, event):
    event.Skip()

#---- Related to the above class ----#
class RenameTabDialog(wx.Dialog):
  def __init__(self, parent):
    wx.Dialog.__init__(self, parent, wx.ID_ANY, 
            'Raname tab id: %d' % parent.tab_id, size=(220,80))
    self.parent = parent
    self.tab_id = parent.tab_id
    main = wx.BoxSizer(wx.VERTICAL)
    self.newname = wx.TextCtrl(self, -1, '', size=(200, 25))
    self.cancel = wx.Button(self, -1, 'Cancel')
    self.append = wx.Button(self, -1, 'Save changes')

    main.Add(self.newname, -1, flag=wx.ALL, border=5)
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(self.cancel, -1, flag=wx.ALL, border=5)
    sizer.Add(self.append, -1, flag=wx.ALL, border=5)
    main.Add(sizer)
    
    self.cancel.Bind(wx.EVT_BUTTON, self.onCancel)
    self.append.Bind(wx.EVT_BUTTON, self.onRename)
    self.SetSizer(main)

  def onCancel(self, event):
    self.Destroy()

  def onRename(self, event):
    title = self.newname.GetValue()
    if len(title)<=0: 
      self.Destroy()
    else:
      self.parent.SetPageText(self.tab_id, title)
      self.Destroy()



'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| Menubar class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class FileMenu:
  #----------------------------------------------------------------------
  def __init__(self, rafiki):
    ''' File menu... '''
    file = wx.Menu()
    file.Append(ID_NEW,    "&New project\tCtrl+N", "New project")
    file.Append(ID_NEWTAB, "&Add tab\tCtrl+T",     "New project")
    file.Append(ID_OPEN,   "&Open\tCtrl+O",        "Open a project")
    file.Append(ID_RECENT, "Open &recent",         "Reopen a poject")
    file.Append(ID_SAVE,   "&Save\tCtrl+S",        "Save project")
    file.Append(ID_SAVEAS, "Save &as...",          "Save project as...")
    file.AppendSeparator()
    file.Append(ID_EXIT,   "E&xit\tCtrl+Q", "Terminate the program")


    ''' Project '''
    project = wx.Menu()
    project.Append(ID_START, "&Run\tCtrl+B",  "Start your script")
    project.Append(ID_STOP, "&Stop\tCtrl+E",  "Stop your script")
    project.AppendSeparator()
    project.Append(ID_FIND, "&Find\tCtrl+F",        "Find text")
    project.Append(ID_REPLACE, "&Find 'n' replace\tCtrl+H",  "Find and replace text")
    project.Append(ID_GOTO, "&Go to line\tCtrl+G",  "Jump to line...")
      
    ''' Tools '''
    tools = wx.Menu()
    tools.Append(ID_PICKCOLOR, "&Pick Color",       "Select colors from screen")
    tools.Append(ID_PICKBMP,   "Pick &Bitmap",      "Select bitmap from screen")
    tools.Append(ID_PRTSCN,    "&Take Screenshoot", "Select colors from screen")
    tools.AppendSeparator()
    tools.Append(ID_BMPToStr,  "&Bitmap To String", "Bitmap to base64 string")
    tools.Append(ID_StrToBMP,  "&String To Bitmap", "Base64 string to bitmap")
    tools.Append(ID_DTMEditor, "&DTM Creator", "Create a deformable template model")
    tools.AppendSeparator()
    tools.Append(ID_NUMBERS,   "&Calculator", "A simple calculator when needed")

    ''' Preferences '''
    preferenses = wx.Menu()
    preferenses.Append(ID_SYNTAXCTRL, "&Syntax highligther", "Customize the syntax colors")
    preferenses.Append(ID_OPTIONS,    "&Options\tCtrl+F1",   "Configure Rafiki")

    ''' Help/About menu '''
    help = wx.Menu()
    help.Append(ID_WEB,  "&Forums",  "A link to the rafiki forums")
    help.Append(ID_ABOUT,  "&About",  "Information about this program")
     

    ''' Creating the menubar '''
    menu = wx.MenuBar()
    menu.Append(file, "&File")
    menu.Append(project, "&Project")
    menu.Append(tools, "&Tools")
    menu.Append(preferenses, "Prefere&nces")
    menu.Append(help, "&Help")
     
    # APPEND THE MENUBAR 
    rafiki.SetMenuBar(menu)


    ''' Define the code to be run when a menu option is selected '''
    # Filemenu
    wx.EVT_MENU(rafiki, ID_NEW,     rafiki.onNewDoc)
    wx.EVT_MENU(rafiki, ID_NEWTAB,  rafiki.onNewTab)
    wx.EVT_MENU(rafiki, ID_OPEN,    rafiki.onOpen)
    wx.EVT_MENU(rafiki, ID_SAVE,    rafiki.onSave)
    wx.EVT_MENU(rafiki, ID_SAVEAS,  rafiki.onSaveAs)
    wx.EVT_MENU(rafiki, ID_EXIT,    rafiki.onExit)

    # Projectmenu
    wx.EVT_MENU(rafiki, ID_START, rafiki.runScript)
    wx.EVT_MENU(rafiki, ID_STOP,  rafiki.killScript)
    wx.EVT_MENU(rafiki, ID_FIND,  rafiki.onFind)

    # Toolmenu
    wx.EVT_MENU(rafiki, ID_PICKCOLOR, rafiki.colorPicker)
    wx.EVT_MENU(rafiki, ID_PICKBMP,   rafiki.bmpPicker)
    wx.EVT_MENU(rafiki, ID_PRTSCN,    rafiki.bmpPicker)
    wx.EVT_MENU(rafiki, ID_BMPToStr,  rafiki.bmp2str)
    wx.EVT_MENU(rafiki, ID_StrToBMP,  rafiki.str2bmp)
    wx.EVT_MENU(rafiki, ID_DTMEditor, rafiki.dtmEditor)
    wx.EVT_MENU(rafiki, ID_NUMBERS,   rafiki.calculator)

    # Preferences
    wx.EVT_MENU(rafiki, ID_SYNTAXCTRL, rafiki.syntaxEditor)
    wx.EVT_MENU(rafiki, ID_OPTIONS,    rafiki.optionMenu)

    # Helpmenu
    wx.EVT_MENU(rafiki, ID_ABOUT, rafiki.onAbout)



'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| This class defines the toolbar
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class Toolbar:
  #----------------------------------------------------------------------
  def __init__(self, rafiki):
    toolbar = rafiki.CreateToolBar()

    ''' FILE MENU '''
    toolbar.AddSimpleTool(ID_NEW, wx.Image(ICONS + 'document-new.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'New', 'Create a new project')

    toolbar.AddSimpleTool(ID_OPEN, wx.Image(ICONS + 'document-open.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Open', 'Open a new project')

    toolbar.AddSimpleTool(ID_SAVE, wx.Image(ICONS + 'document-save.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Save', 'Save your current project')

    toolbar.AddSeparator()

    ''' SCRIPT MENU '''
    toolbar.AddSimpleTool(ID_START, wx.Image(ICONS + 'start.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Run', 'Run the script')

    toolbar.AddSimpleTool(ID_STOP, wx.Image(ICONS + 'stop.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Stop', 'Stop the script')

    toolbar.AddSeparator()

    ''' TOOL MENU '''
    toolbar.AddSimpleTool(ID_PICKCOLOR, wx.Image(ICONS + 'color.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Colorpicker', 'Select color')

    toolbar.AddSimpleTool(ID_WINDOW, wx.Image(ICONS + 'area.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Target window', 'Select targetwindow')

    toolbar.AddSimpleTool(ID_PRTSCN, wx.Image(ICONS + 'screen.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Printscreen', 'Take a screenshot')

    toolbar.AddSimpleTool(ID_NUMBERS, wx.Image(ICONS + 'calculator.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Calculator', 'Calculate something...')

    toolbar.AddSeparator()

    ''' RAFIKI MENU '''
    toolbar.AddSimpleTool(ID_CLEAR, wx.Image(ICONS + 'clear.png',
        wx.BITMAP_TYPE_PNG).ConvertToBitmap(), 'Clear debug', 'Clear the debug box')


    toolbar.Realize()


    ''' A few events needs to be added here as well '''
    wx.EVT_MENU(rafiki, ID_CLEAR, rafiki.clearDebug)
    wx.EVT_MENU(rafiki, ID_WINDOW, rafiki.windowArea)



'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| This class defines the "scriptengine" | Running & stopping scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
class ScriptEngine:
  #----------------------------------------------------------------------
  def __init__(self, wxRafiki):
    self.rafiki = wxRafiki

  def removeTempFiles(self):
    rafiki = self.rafiki
    folder = os.path.dirname(os.path.realpath(__file__))
    for the_file in glob.glob(folder+'/*.tmp'):
      file_path = os.path.join(folder, the_file)
      try:
        if os.path.isfile(file_path):
          os.unlink(file_path)
      except Exception, e:
        pass
        #rafiki.writeLn(e)

  def killscript(self):
    try:
      self.proc.kill()
      self.removeTempFiles()
    except:
      try: self.removeTempFiles()
      except: pass

  def runscript(self, script, wnd):
    self.rafiki.clearDebug(0);
    t = Thread(target=self.__runscript, args=(script, wnd,))
    t.start()

  def __runscript(self, script, wnd):
    #--------------------------------------------------------#
    self.removeTempFiles()
    folder = os.path.dirname(os.path.realpath(__file__))
    #Make a random tempfile
    id = str(randint(1000,99999))
    self.tempfile = "script_"+id+".tmp"
    tmp = open(self.tempfile, 'wb')
    tmp.write(script.encode("utf8"))
    tmp.close()

    #--------------------------------------------------------#
    conf = options.RConfig()
    argument = []

    use_default = conf.getValue('INTERPRETER', 'default', bool)
    hide_warn = conf.getValue('INTERPRETER', 'hidewarn', bool)
    unbuffered = conf.getValue('INTERPRETER', 'unbuffered', bool)
    #other = conf.getValue('INTERPRETER', 'other', str).split(',')

    #Interpreter
    if use_default: argument.append(sys.executable)
    else: argument.append(conf.getValue('INTERPRETER', 'path'))

    #Buffered?
    if unbuffered: argument.append('-u')

    #Hide warnings (windows only)
    if platform.system() == 'Windows':
      if hide_warn: 
        argument.append('-W ignore::DeprecationWarning')

    argument.append(self.tempfile)
    argument.extend([str(wnd[0]), str(wnd[1]), str(wnd[2]), str(wnd[3])])

    blockwords = ['Xlib.protocol.request.QueryExtension']

    #----------------------- GOGOGO! -----------------------#
    wx.CallAfter(Publisher.sendMessage, "update", "[Starting new process...]")
    try:
      start = time.time()
      errormsg = ''
      startupinfo = None

      ''' remove the terminal on windows '''
      if platform.system() == 'Windows':
          startupinfo = subprocess.STARTUPINFO()
          startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
          startupinfo.wShowWindow = _subprocess.SW_HIDE

      self.proc = subprocess.Popen(argument, 
                                   startupinfo = startupinfo,
                                   stdout = subprocess.PIPE, 
                                   stderr = subprocess.PIPE, 
                                   shell = False)

      for line in iter(self.proc.stdout.readline, ''):
          if not ' '.join(line.split()) in blockwords:
            wx.CallAfter(Publisher.sendMessage, "update", "%s" % line)

      for line in iter(self.proc.stderr.readline, ''):
          errormsg += "  "+line

      time_used = float(time.time()-start)    
      self.proc.stdout.close() 

      if errormsg != '':
          wx.CallAfter(Publisher.sendMessage, "update", errormsg)
          wx.CallAfter(Publisher.sendMessage, "update", "[An error occured]")

      else: 
        success = "[Successfully executed in %f sec]" % time_used
        wx.CallAfter(Publisher.sendMessage, "update", success)

    except Exception as e:
      wx.CallAfter(Publisher.sendMessage, "update", "%s" % e)

    self.removeTempFiles()
    wx.CallAfter(Publisher.sendMessage, "update", False)



'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
| Just a plain old "about"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
class AboutFrame(wx.Dialog):
  #----------------------------------------------------------------------
  def __init__(self, parent=None):
    self.title = "About Rafiki (Beta)"
    wx.Dialog.__init__(self, wx.GetApp().TopWindow, 
                      id=wx.ID_ANY, 
                      title="About", 
                      size=(550,300))
    self.CentreOnParent(wx.BOTH)
    html = wxHTML(self)
    html.SetPage("""
            <h2>Rafiki Pre-Alpha</h2>
            <p>
            Rafiki is a program used to repeat certain (complicated) tasks. 
            Typically these tasks involve using the mouse and keyboard. <br><br>
            Rafiki is programmable, which means you can design your own logic 
            and steps that Rafiki will follow, based upon certain input.<br><br>
            Rafiki is also Open Source, released under the GNU GPL v3 lisence.</p>
            <p>Created by Jarl <i>"slacky"</i> Holta.</p>
            <p><b>Requirements:</h3><br /></p>
            - <b><a href="http://www.python.org">Python 2.7</a></b><br>
            - <b><a href="http://www.wxpython.org">wxPython 2.8</a></b><br />
            - <b><a href="http://pypi.python.org/pypi/Pillow/">
                 Python Imaging Library (pillow or PIL)</a></b>
            """)
 
class wxHTML(wx.html.HtmlWindow):
     def OnLinkClicked(self, link):
         webbrowser.open(link.GetHref())


# If it's not an include then run it
if __name__ == '__main__':
  app = App(False)
  app.MainLoop()