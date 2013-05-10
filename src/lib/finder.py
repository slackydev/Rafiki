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

 --- Computer vision (RAW Version) for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
from PIL import Image
from colormath import rgb_to_cielab, rgb_to_hsb, rgb_to_cielch
from random import choice
import sys

from ..Interfaces import grabScreen, get_pixel_colour

AREA = {
	'x1': int(sys.argv[1]), 'y1': int(sys.argv[2]),
	'x2': int(sys.argv[3]), 'y2': int(sys.argv[4])
}

CACHE_HSB = {}
CACHE_LAB = {}
CACHE_LCH = {}


colormode = 1
modifiers = {
    'rgb_r': 1, 'rgb_g': 1, 'rgb_b': 1, 
    'hsb_h': 1, 'hsb_s': 1, 'hsb_b': 1,
    'lab_l': 1, 'lab_a': 1, 'lab_b': 1,
    'lch_l': 1, 'lch_c': 1, 'lch_h': 1
}

def whipe_cache():
    global CACHE_HSB, CACHE_LAB, CACHE_LCH
    CACHE_HSB = {}
    CACHE_LAB = {}
    CACHE_LCH = {}

def get_cache(i):
    if i == 2:
        return CACHE_HSB
    if i == 4:
        return CACHE_LAB 
    if i == 6:
        return CACHE_LCH

"""---------------------------------------------------------------"""
# ALLOWING USERS TO CHOOSE BEST COLOR MODE & MODIFIERS
"""---------------------------------------------------------------"""
def set_mode(mode):
    # Set a new colormode.
    global colormode
    if mode in range(0, 8):
        colormode = mode
    else:
        print "Colormode set to default"
        colormode = 1

def get_mode():
    # Get Current colormode.
    return colormode

""" -------------------- SET MODIFIERS -------------------- """
### 
def set_tol_modifier_0(RMod,GMod,BMod):
    # Set RGB-modifiers to...
    mod = modifiers
    mod['rgb_r'] = RMod
    mod['rgb_g'] = GMod
    mod['rgb_b'] = BMod
 
def set_tol_modifier_2(HMod,SMod,BMod):
    # Set LAB-modifiers to...
    mod = modifiers
    mod['hsb_h'] = HMod
    mod['hsb_s'] = SMod
    mod['hsb_b'] = BMod

def set_tol_modifier_4(LMod,AMod,BMod):
    # Set LAB-modifiers to...
    mod = modifiers
    mod['lab_l'] = LMod
    mod['lab_a'] = AMod
    mod['lab_b'] = BMod

def set_tol_modifier_6(LMod,CMod,HMod):
    #Set LAB-modifiers to...
    mod = modifiers
    mod['lch_l'] = LMod
    mod['lch_c'] = CMod
    mod['lch_h'] = HMod

""" -------------------- GET MODIFIERS -------------------- """
### 
def get_tol_modifier_0():
    # Get Current color modifiers (RGB).
    mod = modifiers
    return mod['rgb_r'], mod['rgb_g'], mod['rgb_b']

def get_tol_modifier_2():
    #Get Current color modifiers (LAB).
    mod = modifiers
    return mod['hsb_h'], mod['hsb_s'], mod['hsb_b']

def get_tol_modifier_4():
    # Get Current color modifiers (LAB).
    mod = modifiers
    return mod['lab_l'], mod['lab_a'], mod['lab_b']

def get_tol_modifier_6():
    # Get Current color modifiers (LAB).
    mod = modifiers
    return mod['lch_l'], mod['lch_c'], mod['lch_h']

    # ----------
def reset_color_modifiers():
    """ Reset ColorModifiers. """
    modifiers = {
        'rgb_r': 1, 'rgb_g': 1, 'rgb_b': 1, 
        'lch_l': 1, 'lch_c': 1, 'lch_h': 1, 
        'lab_l': 1, 'lab_a': 1, 'lab_b': 1,
        'hsb_h': 1, 'hsb_s': 1, 'hsb_b': 1,
    }

""" ================== END OF MODIFIERS =================== """

"""---------------------------------------------------------------"""
# CONVERT COLORS TO CORRECT MODE
"""---------------------------------------------------------------""" 
def conv_to_mode(color):
      #Used in "finding-functions" to autconvert colorspace.
    if colormode in (0,1): #R, G, B
        return color

    elif colormode in (2,3): #H, S, B
        return rgb2hsb(color[0], color[1], color[2])

    elif colormode in (4,5): #L, A, B
        return rgb2lab(color[0], color[1], color[2])

    elif colormode in (6,7): #L, C, H
        return rgb2lch(color[0], color[1], color[2])

"""---------------------------------------------------------------"""
# COMPARISON ALGORITHMS
"""---------------------------------------------------------------""" 
def compare(c1, c2, tol):
    #-------- RGB MODES --------#
    if colormode == 0:
        return (abs(c1[0] - c2[0]) <= tol and \
                abs(c1[1] - c2[1]) <= tol and \
                abs(c1[2] - c2[2]) <= tol )  
   
    elif colormode == 1:
        r = c1[0] - c2[0]
        g = c1[1] - c2[1]
        b = c1[2] - c2[2]
        return ((r*r + g*g + b*b) <= tol);

    #-------- HSB MODES  --------#
    elif colormode == 2:
        (h,s,b) = rgb2hsb(c2[0], c2[1], c2[2])
        return (abs(((c1[2] - h + 50) % 100) - 50) <= tol and \
                abs(s - c1[1]) <= tol and \
                abs(b - c1[2]) <= tol)

    elif colormode == 3:
        (h,s,b) = rgb2hsb(c2[0], c2[1], c2[2])
        H = ((c1[0] - h + 50) % 100) - 50
        S = c1[1] - s
        B = c1[2] - b
        return ((H*H + S*S + B*B) <= tol)
        
    #-------- LAB MODES  --------#   
    elif colormode == 4:
        (l,a,b) = rgb2lab(c2[0], c2[1], c2[2])
        return (abs(l - c1[0]) <= tol and \
                abs(a - c1[1]) <= tol and \
                abs(b - c1[2]) <= tol);

    elif colormode == 5:
        (l,a,b) = rgb2lab(c2[0], c2[1], c2[2])
        L = c1[0] - l
        A = c1[1] - a
        B = c1[2] - b
        return ((L*L + A*A + B*B) <= tol);
        
    #------- LCH MODES --------# 
    elif colormode == 6:
        (l,c,h) = rgb2lch(c2[0], c2[1], c2[2])
        return ((abs(l - c1[0]) <= tol) and \
                (abs(c - c1[1]) <= tol) and \
                (abs(((c1[2] - h + 180) % 360) - 180) <= tol));

    elif colormode == 7:
        (l,c,h) = rgb2lch(c2[0], c2[1], c2[2])
        L = c1[0] - l
        C = c1[1] - c
        H = ((c1[2] - h + 180) % 360) - 180;
        return ((L*L + C*C + H*H) <= tol);

#--------------------------------------------------------------------
def similar(color1, color2, tol):
    ''' compare to colors '''
    color1 = conv_to_mode((r,g,b))
    return compare(color1, color2, tol)

#--------------------------------------------------------------------
def get_pixel(x, y):
    ''' get color of a pixel on the screen '''
    r,g,b = get_pixel_colour(x, y)
    return (r,g,b)

#--------------------------------------------------------------------
def find_multi(color, XS,YS,XE,YE, tol=1, get=-1, image=False):
    if get == -1: get = abs(XE-XS) * abs(YE-YS)  
    if not image:
        image = grabScreen(AREA['x1'], AREA['y1'], AREA['x2'], AREA['y2'])

    color1 = conv_to_mode(color)
    pts = []
    pix = image.load()
    for x in xrange(XS,XE):
        for y in xrange(YS,YE):
            color2 = pix[x,y]
            if compare(color1, color2, tol):
                pts.append((x,y))
                if len(pts)>=get:
                    return pts
                    #     
    return pts
    
#--------------------------------------------------------------------   
def find(color, XS,YS,XE,YE, tol=1, image=False):
    return find_multi(color, XS,YS,XE,YE, tol=tol, get=1, image=image)

#--------------------------------------------------------------------
def find_multi_spiral(color, XS,YS,XE,YE, tol=1, get=-1, image=False):
    if get == -1: get = abs((XS-XE)) * abs((YS-YE))
    if not image:
        image = grabScreen(AREA['x1'], AREA['y1'], AREA['x2'], AREA['y2'])
        
    color1 = conv_to_mode(color)
        
    sx,sy,dx,dy = 0,0,0,-1
    WX,HY = (XE+XS)/2, (YE+YS)/2
    pts = []
    pix = image.load()
    for i in xrange(max((XE-XS), (YE-YS))**2): 
        if (-WX < sx <= WX) and (-HY < sy <= HY):

            color2 = pix[WX+sx, HY+sy]
            if compare(color1, color2, tol):
                pts.append((WX+sx, HY+sy))
                if len(pts)>=get:
                    return pts
                    
        if sx == sy or (sx < 0 and sx == -sy) or (sx > 0 and sx == 1-sy):
            dx, dy = -dy, dx
        sx, sy = sx+dx, sy+dy
        
    return pts

#--------------------------------------------------------------------
def find_spiral(color, XS,YS,XE,YE, tol=1, image=False):
    return find_multi_spiral(color, XS,YS,XE,YE, tol=tol, get=1, image=image)



"""---------------------------------------------------------------"""
# INTERNAL COLOR-CONVERTING - CACHED
"""---------------------------------------------------------------"""   
def rgb2hsb(R, G, B):
    ''' RGB-space to HSB-space '''
    if (R, G, B) in CACHE_HSB:
        return CACHE_HSB[(R, G, B)]
    else:
        (h,s,b) = rgb_to_hsb(R,G,B)
        CACHE_HSB[(R, G, B)] = (h,s,b)
        return (h,s,b)

def rgb2lab(R, G, B):
    ''' RGB-space to LAB-space '''
    if (R, G, B) in CACHE_LAB:
        return CACHE_LAB[(R, G, B)]
    else:
        (l,a,b) = rgb_to_cielab(R,G,B)
        CACHE_LAB[(R, G, B)] = (l,a,b)
        return (l,a,b)

def rgb2lch(R, G, B):
    ''' RGB-space to LCH-space '''
    if (R, G, B) in CACHE_LCH:
        return CACHE_LCH[(R, G, B)]
    else:
        (l,c,h) = rgb_to_cielch(R,G,B)
        CACHE_LCH[(R, G, B)] = (l,c,h)
        return (l,c,h)