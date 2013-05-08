#!/usr/bin/python
'''---------------------------------------------------------------
@ todo: A LOT! - On mouse click, return current hWin and rect.
        Much planning is needed as well.
        - Split it up, one file for linux, and one for windows?
        - On Windows we can use WxPythons drawrect on screen.
---------------------------------------------------------------'''
from Xlib import X, display, Xutil
import Xlib
import src.Interfaces as iface
import time

dsp = display.Display()

#---- Draw a rect on the screen ----
def drawRect(width, pos, size):
    
    screen = dsp.screen()

    colormap = screen.default_colormap
    color = colormap.alloc_color(0, 0, 65535)
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


#---- Draw the area box under the mouse ----
def drawTargetArea(maxTimer=10):
    M = iface.Mouse()
    window = iface.getWindowFromPoint(M.position())
    prev_pos = window['pos']
    prev_obj = window['obj']
    prev_size = window['size']
    line_width = 3
    drawRect(line_width, prev_pos,prev_size)

    start = time.time()
    while True:
        window = iface.getWindowFromPoint(M.position())
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

        if (start+maxTimer) < time.time():
            break;

    drawRect(line_width, prev_pos, prev_size)
    return (prev_obj, prev_pos, prev_size)

#-----------------------------------------------------
if __name__ == '__main__':
  print drawTargetArea(10)