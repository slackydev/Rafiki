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

 --- Mouse control for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
from __future__ import division
from math import sqrt, hypot
from random import randrange, uniform, gauss
import random as r
from time import sleep
import sys

from ..Interfaces import Mouse

sqrt3 = sqrt(3)
sqrt5 = sqrt(5)

mice = Mouse()
start_pos = int(sys.argv[1]), int(sys.argv[2])

#-------------------------------------------------------------------
def wait_r(k,v):
    """ sleep everything for X time 
    """
    time = round(uniform(k,v), 4)
    return sleep(time)

#-------------------------------------------------------------------
def get_position():
    """ Get mouse position within the selected target
    """
    x, y = mice.position()
    x -= start_pos[0]
    y -= start_pos[1]
    return x,y

#-------------------------------------------------------------------
def set_position(x,y):
    """ set mouse position based on the selected target
    """
    x += start_pos[0]
    y += start_pos[1]
    mice.move(x,y)

#-------------------------------------------------------------------
def click(btn):
    """ click a mouse-btn at current crossair position
    """
    x, y = mice.position()
    mice.press(x,y, btn)
    sleep(round(gauss(0.060, 0.021),4))
    mice.release(x,y, btn)

#-------------------------------------------------------------------
def button_state(btn):
    print 'Not implemented yet'
    pass

#-------------------------------------------------------------------
def button_down(btn):
    """ mouse button down at current positon
    """
    x, y = mice.position()
    mice.press(x,y, btn)

#-------------------------------------------------------------------    
def button_up(btn):
    """ mouse button down at current positon
    """
    x, y = mice.position()
    mice.release(x,y, btn)

#-------------------------------------------------------------------
def move_click(x,y, btn, rand=(0,0)):
    """ move the mouse and click a buttn at at point
    """
    try: 
        x += randrange(-rand[0],rand[0])
        y += randrange(-rand[1],rand[1])
    except ValueError: 
        pass

    move(x,y)
    sleep(round(gauss(0.020, 0.014),4))
    return click(btn)

#-------------------------------------------------------------------
def move(x,y, speed=12, rand=(0,0), skipclose=1):
    ''' A smart mouse movement function written by Benjamin J. Land
        # https://github.com/BenLand100

        Convertet to Python by Yumekui and Author
    '''
    #---------------------------------------------------------------
    def Move_(x0, y0, x, y, gravity, wind, minWait, maxWait, maxStep, targetArea):
        x1,y1=x0,y0
        veloX = veloY = windX = windY = 0
        dist = sqrt((x-x0)*(x-x0) + (y-y0)*(y-y0))
        while 1 <= dist:
            wind = min(wind, dist)
            if dist >= targetArea:
                windX = windX/sqrt3 + (r.random()*(wind*2. + 1.) - wind)/sqrt5
                windY = windY/sqrt3 + (r.random()*(wind*2. + 1.) - wind)/sqrt5
            else:
                windX = windX/sqrt3
                windY = windY/sqrt3
                if 3 > maxStep:
                    maxStep = r.random()*3. + 3.
                else:
                    maxStep = maxStep/sqrt5
                
            veloX += windX + gravity*(x - x0)/dist
            veloY += windY + gravity*(y - y0)/dist    
            veloMag = sqrt((veloX)*(veloX) + (veloY)*(veloY))
            if veloMag > maxStep:
                randomDist = maxStep/2. + r.random()*(maxStep/2.)
                veloX = (veloX/veloMag)*randomDist
                veloY = (veloY/veloMag)*randomDist
            x0 += veloX
            y0 += veloY
            mx = int(round(x0))
            my = int(round(y0))
            
            if (cx != mx) or (cy != my):
                set_position(mx, my)

            step = hypot(x0 - cx, y0 - cy);
            sleep(round((maxWait - minWait)/1000)*round((step/maxStep)/1000) + minWait/1000)
            dist = sqrt((x-x0)*(x-x0) + (y-y0)*(y-y0))
        return cx, cy

    #---------------------------------------------------------------
    spdev = (r.random()*15. + 15.)/float(speed)

    cx, cy = get_position()
    (stdevx, stdevy) = rand

    #skip if mouse is already close to target unless told to not do so
    if skipclose and abs(cx-x) < 3 and abs(cy-y) < 3:
        return cx, cy
    if stdevx != 0:
        x = randrange(x-stdevx, x+stdevx)
    if stdevy != 0:
        y = randrange(y-stdevx, y+stdevx)
    
    Move_(cx, cy, x, y, 9.81, 2.,5./spdev,10/spdev,10*spdev,8*spdev)
    
#-------------------------------------------------------------------
def box(box, btn=False):
    """ Move mouse to a random point within a given box 
    """
    x1,y1,x2,y2 = box
    try: 
        x,y = randrange(x1, x2), randrange(y1, y2)
    except ValueError: 
        x,y = x1-x2, y1-y2
    
    move(x,y)
    if btn: click(btn)
