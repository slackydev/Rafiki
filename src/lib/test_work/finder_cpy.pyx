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

 --- Computer vision (CPy Version) for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
from PIL import Image
from random import choice
import sys, colorsys

from ..Interfaces import grabScreen, get_pixel_colour
import math


cdef int byte
cdef float sixteenDiv116, oneDiv3

XYZ_B = {}
for byte in range(256):
    XYZ_B[byte] = (((byte/255.0) + 0.055) / 1.055) ** 2.4

sixteenDiv116 = 16.0 / 116.0
oneDiv3 = 1.0/3.0

AREA = {
    'x1': int(sys.argv[1]), 'y1': int(sys.argv[2]),
    'x2': int(sys.argv[3]), 'y2': int(sys.argv[4])
}

CACHE_LAB = {}
CACHE_LCH = {}
cdef int colormode = 1


#Private colormath
'''--------------------------------------------------------------------------------------'''
#-------------------------------------------------#
def rgb_to_xyz(int R, int G, int B):
    '''
    Convert from RGB to XYZ.
    '''
    cdef float vR, vG, vB, X, Y, Z

    vR = (R / 255.0)
    vG = (G / 255.0)
    vB = (B / 255.0)

    if vR > 0.04045:
        vR = XYZ_B.get(R) 
    else:
        vR /= 12.92

    if vG > 0.04045:
        vG = XYZ_B.get(G) 
    else:
        vG /= 12.92

    if vB > 0.04045:
        vB = XYZ_B.get(B) 
    else:
        vB /= 12.92

    vR *= 100
    vG *= 100
    vB *= 100

    #Observer. = 2 deg, Illuminant = D65
    X = vR * 0.4124 + vG * 0.3576 + vB * 0.1805
    Y = vR * 0.2126 + vG * 0.7152 + vB * 0.0722
    Z = vR * 0.0193 + vG * 0.1192 + vB * 0.9505

    return X,Y,Z

#-------------------------------------------------#
def xyz_to_cielab(float X, float Y, float Z):
    '''
    Convert from XYZ to CIE-L*a*b*
    '''
    cdef float vX, vY, vZ, L, a, b

    vX = X / 95.047
    vY = Y / 100.000
    vZ = Z / 108.883

    if vX > 0.008856: vX **= (oneDiv3) 
    else: vX = (7.787 * vX) + sixteenDiv116
    
    if vY > 0.008856: vY **= oneDiv3
    else: vY = (7.787 * vY) + sixteenDiv116
    
    if vZ > 0.008856: vZ **= (oneDiv3)
    else: vZ = (7.787 * vZ) + sixteenDiv116

    L = (116 * vY) - 16.0
    a = 500.0 * (vX - vY)
    b = 200.0 * (vY - vZ)

    return L, a, b

#-------------------------------------------------#
def rgb_to_cielab(int R, int G, int B):
    '''
    Convert from RGB to CIE-L*a*b*.
    '''
    cdef float X,Y,Z
    X,Y,Z = rgb_to_xyz(R,G,B)
    return xyz_to_cielab(X,Y,Z)

#-------------------------------------------------#
def rgb_to_cielch(int R, int G, int BB):
    cdef float L,C,H,A,B
    L,A,B = rgb_to_cielab(R,G,BB);
  
    C = math.sqrt(A*A + B*B)
    H = math.atan2(B,A)
    if (H > 0): H = (H / 3.14159265) * 180
    else: H = 360 - (abs(H) / 3.14159265) * 180
    return L,C,H

def rgb_to_hsl(int R, int G, int B):
    cdef float h,s,l, maxc, minc, rc,gc,bc,delta
    
    r = (R / 255.000)
    g = (G / 255.000)
    b = (B / 255.000)

    maxc = max(r, max(g, b))
    minc = min(r, min(g, b))
    delta = maxc-minc

    l = (minc+maxc)/2.0
    if minc == maxc:
        return 0,0,l * 100
    else:
        if l <= 0.5:
            s = delta / (maxc+minc)
        else:
            s = delta / (2.0-delta)
        rc = (maxc-r) / delta
        gc = (maxc-g) / delta
        bc = (maxc-b) / delta
        if r == maxc:
            h = bc-gc
        elif g == maxc:
            h = 2.0+rc-bc
        else:
            h = 4.0+gc-rc
    h = (h/6.0) % 1.0#

    return h*100, s*100, l*100

'''--------------------------------------------------------------------------------------'''


#Color finding functions
'''--------------------------------------------------------------------------------------'''
def whipe_cache():
    global CACHE_LAB, CACHE_LCH
    CACHE_LAB = {}
    CACHE_LCH = {}

def get_cache(i='lab'):
    if i == 'lab':
        return CACHE_LAB 
    if i == 'lch':
        return CACHE_LCH

"""---------------------------------------------------------------"""
# ALLOWING USERS TO CHOOSE BEST COLOR MODE & MODIFIERS
"""---------------------------------------------------------------"""
def set_mode(int mode):
    # Set a new colormode.
    global colormode
    if mode in range(0, 8):
        colormode = mode
        return True
    else:
        print "Colormode set to default"
        colormode = 1
        return False
    

def get_mode():
    # Get Current colormode.
    return colormode

"""---------------------------------------------------------------"""
# CONVERT COLORS TO CORRECT MODE
"""---------------------------------------------------------------""" 
def conv_to_mode(color):
      #Used in "finding-functions" to autconvert colorspace.
    if colormode in (0,1): #R, G, B
        return color

    elif colormode in (2,3): #H, S, B
        return rgb_to_hsl(color[0], color[1], color[2])

    elif colormode in (4,5): #L, A, B
        return rgb2lab(color[0], color[1], color[2])

    elif colormode in (6,7): #L, C, H
        return rgb2lch(color[0], color[1], color[2])

"""---------------------------------------------------------------"""
# COMPARISON ALGORITHMS
"""---------------------------------------------------------------""" 
cdef int compare(c1, c2, int tol):
    cdef int r,g,bb
    cdef float h,s,b,H,S,B,l,a,c,L,A

    #-------- RGB MODES --------#
    if colormode == 0:
        return (abs(c1[0] - c2[0]) <= tol and \
                abs(c1[1] - c2[1]) <= tol and \
                abs(c1[2] - c2[2]) <= tol) 
   
    elif colormode == 1:
        r = c1[0] - c2[0]
        g = c1[1] - c2[1]
        bb = c1[2] - c2[2]
        return ((r*r + g*g + bb*bb) <= tol);

    #-------- HSB MODES  --------#
    elif colormode == 2:
        h,s,b = rgb_to_hsl(c2[0], c2[1], c2[2])
        if c1[0] > h: h = min(c1[0] - h, abs(c1[0] - (h + 100)))
        else: h = min(h - c1[0], abs(h - (c1[0] + 100)))
        return (abs(h - c1[0]) <= tol and \
                abs(s - c1[1]) <= tol and \
                abs(b - c1[2]) <= tol)
        return False

    elif colormode == 3:
        (h,s,b) = rgb_to_hsl(c2[0], c2[1], c2[2])
        if c1[0] > h: H = min(c1[0] - h, abs(c1[0] - (h + 100)))
        else: H = min(h - c1[0], abs(h - (c1[0] + 100)))
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
                (abs(((c1[2] - h + 180) % 360) - 180) <= tol))

    elif colormode == 7:
        (l,c,h) = rgb2lch(c2[0], c2[1], c2[2])
        L = c1[0] - l
        C = c1[1] - c
        H = ((c1[2] - h + 180) % 360) - 180
        return ((L*L + C*C + H*H) <= tol);

#--------------------------------------------------------------------
def similar(color1, color2, int tol):
    ''' compare to colors '''
    color1 = conv_to_mode(color1)
    return compare(color1, color2, tol)

#--------------------------------------------------------------------
def get_pixel(int x, int y):
    ''' get color of a pixel on the screen '''
    r,g,b = get_pixel_colour(x, y)
    return (r,g,b)

#--------------------------------------------------------------------
def find_multi(color, int XS,int YS,int XE,int YE, int tol=1, int get=-1, image=False):
    cdef int x,y

    if get == -1: get = abs(XE-XS) * abs(YE-YS)
    if not image:
        image = grabScreen(AREA['x1'], AREA['y1'], AREA['x2'], AREA['y2'])

    color1 = conv_to_mode(color)
    pts = []
    pix = image.load()
    for x from XS <= x < XE:
        for y from YS <= y < YE:
            color2 = pix[x,y]
            if compare(color1, color2, tol):
                pts.append((x,y))
                if len(pts)>=get:
                    return pts
                    #     
    return pts
    
#--------------------------------------------------------------------   
def find(color, int XS,int YS,int XE,int YE, int tol=1, image=False):
    return find_multi(color, XS,YS,XE,YE, tol=tol, get=1, image=image)

#--------------------------------------------------------------------
def find_multi_spiral(color, int XS,int YS,int XE,int YE, int tol=1, int get=-1, image=False):
    cdef int i, sx,sy,dx,dy,WX,HY
    cdef long size
    if get == -1: get = abs((XS-XE)) * abs((YS-YE))
    if not image:
        image = grabScreen(AREA['x1'], AREA['y1'], AREA['x2'], AREA['y2'])
        
    color1 = conv_to_mode(color)
        
    sx,sy,dx,dy = 0,0,0,-1
    WX,HY = (XE+XS) // 2, (YE+YS) // 2
    size = max((XE-XS), (YE-YS)) ** 2
    pts = []
    pix = image.load()
    for i from 0 <= i < size:
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
def find_spiral(color, int XS, int YS,XE,int YE,int tol=1, image=False):
    return find_multi_spiral(color, XS,YS,XE,YE, tol=tol, get=1, image=image)



"""---------------------------------------------------------------"""
# INTERNAL COLOR-CONVERTING - CACHED
"""---------------------------------------------------------------"""   
def rgb2lab(int R, int G, int B):
    ''' RGB-space to LAB-space '''
    cdef float l,a,b
    try:
        l,a,b = CACHE_LAB[(R,G,B)]
    except:
        l,a,b = rgb_to_cielab(R,G,B)
        CACHE_LAB[(R, G, B)] = (l,a,b)
    
    return l,a,b

def rgb2lch(int R, int G, int B):
    ''' RGB-space to LCH-space '''
    cdef float l,c,h
    try:
        l,c,h = CACHE_LCH[(R,G,B)]
    except:
        l,c,h = rgb_to_cielab(R,G,B)
        CACHE_LCH[(R, G, B)] = (l,c,h)
    
    return l,c,h