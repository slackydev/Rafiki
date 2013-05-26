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

 --- Comarison of colors for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
from colormath import rgb_to_cielab, rgb_to_hsb, rgb_to_cielch
from math import sqrt

#standard comparison mode
colormode = 0

"""---------------------------------------------------------------"""
# ALLOWING USERS TO CHOOSE COLOR MODE & MODIFIERS
"""---------------------------------------------------------------"""
def set_mode(mode):
    # Set a new color comparison mode/algo.
    global colormode
    if mode in range(0, 8):
        colormode = mode
    else:
        print "Colormode set to default"
        colormode = 0

def get_mode():
    # Get Current color comparison mode/algo.
    return colormode


"""---------------------------------------------------------------"""
# CONVERT COLORS TO COLORSPACE DEFINED BY `colormode`
"""---------------------------------------------------------------""" 
def conv_to_mode(color):
    if colormode in (0,1): #R, G, B
        return color

    elif colormode in (2,3): #H, S, B
        return rgb2hsb(color[0], color[1], color[2])

    elif colormode in (4,5): #L, A, B
        return rgb2lab(color[0], color[1], color[2])

    elif colormode in (6,7): #L, C, H
        return rgb2lch(color[0], color[1], color[2])

"""---------------------------------------------------------------"""
# COMPARISON OF TWO COLORS BY THE GIVEN ALGORITHM
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
        return sqrt(r*r + g*g + b*b) <= tol;

    #-------- HSB MODES  --------#
    elif colormode == 2:
        return (abs(((c1[2] - h + 50) % 100) - 50) <= tol and \
                abs(s - c1[1]) <= tol and \
                abs(b - c1[2]) <= tol)

    elif colormode == 3:
        H = ((c1[0] - h + 50) % 100) - 50
        S = c1[1] - s
        B = c1[2] - b
        return ((H*H + S*S + B*B) <= tol)
        
    #-------- LAB MODES  --------#   
    elif colormode == 4:
        return (abs(l - c1[0]) <= tol and \
                abs(a - c1[1]) <= tol and \
                abs(b - c1[2]) <= tol);

    elif colormode == 5:
        L = c1[0] - l
        A = c1[1] - a
        B = c1[2] - b
        return ((L*L + A*A + B*B) <= tol);
        
    #------- LCH MODES --------# 
    elif colormode == 6:
        return ((abs(l - c1[0]) <= tol) and \
                (abs(c - c1[1]) <= tol) and \
                (abs(((c1[2] - h + 180) % 360) - 180) <= tol));

    elif colormode == 7:
        L = c1[0] - l
        C = c1[1] - c
        H = ((c1[2] - h + 180) % 360) - 180;
        return ((L*L + C*C + H*H) <= tol);

#--------------------------------------------------------------------
def similar(color1, color2, tol):
    ''' compare to colors '''
    color1 = conv_to_mode(color1)
    color2 = conv_to_mode(color2)
    return compare(color1, color2, tol)