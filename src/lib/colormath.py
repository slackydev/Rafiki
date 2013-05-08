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

 --- Colormath for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The formulas for the functions defined below was obtained from the EasyRGB 
# Website: http://www.easyrgb.com/math.html
#
# PS: Division from python v3.x is faster. Hence the __future__ statement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
from __future__ import division
import math

XYZ_B = {}
for byte in range(256):
    XYZ_B[byte] = (((byte/255.) + 0.055) / 1.055) ** 2.4

#-------------------------------------------------#
def rgb_to_xyz(R, G, B):
    '''
    Convert from RGB to XYZ.
    '''
    vR = (R / 255.)
    vG = (G / 255.)
    vB = (B / 255.)

    if vR > 0.04045:
        #vR = ((vR + 0.055) / 1.055) ** 2.4
        vR = XYZ_B.get(R) 
    else:
        vR /= 12.92

    if vG > 0.04045:
        #vG = ((vG + 0.055) / 1.055) ** 2.4
        vG = XYZ_B.get(G) 
    else:
        vG /= 12.92

    if vB > 0.04045:
        #vB = ((vB + 0.055) / 1.055) ** 2.4
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
def xyz_to_rgb(X, Y, Z):
    ''' 
    Convert from XYZ to RGB. 
    '''
    vX = X / 100
    vY = Y / 100
    vZ = Z / 100

    var_R = vX *  3.2406 + vY * -1.5372 + vZ * -0.4986
    var_G = vX * -0.9689 + vY *  1.8758 + vZ *  0.0415
    var_B = vX *  0.0557 + vY * -0.2040 + vZ *  1.0570

    if var_R > 0.0031308: 
        var_R = 1.055 * ( var_R ** ( 1. / 2.4 ) ) - 0.055
    else:
        var_R *= 12.92

    if var_G > 0.0031308:
        var_G = 1.055 * ( var_G ** ( 1. / 2.4 ) ) - 0.055
    else:
        var_G *= 12.92

    if var_B > 0.0031308:
        var_B = 1.055 * ( var_B ** ( 1. / 2.4 ) ) - 0.055
    else:
        var_B *= 12.92

    R = int(var_R * 255) #round is to slow...
    G = int(var_G * 255) #round is to slow...
    B = int(var_B * 255) #round is to slow...

    return R, G, B


#-------------------------------------------------#
def xyz_to_cielab(X, Y, Z):
    '''
    Convert from XYZ to CIE-L*a*b*
    '''
    vX = X / 95.047
    vY = Y / 100.000
    vZ = Z / 108.883

    if vX > 0.008856: vX **= (1./3.)
    else: vX = (7.787 * vX) + (16. / 116.)
    
    if vY > 0.008856: vY **= (1./3.)
    else: vY = (7.787 * vY) + (16. / 116.)
    
    if vZ > 0.008856: vZ **= (1./3.)
    else: vZ = (7.787 * vZ) + (16. / 116.)

    CIE_L = (116 * vY) - 16.
    CIE_a = 500. * (vX - vY)
    CIE_b = 200. * (vY - vZ)

    return CIE_L, CIE_a, CIE_b


#-------------------------------------------------#
def cielab_to_xyz(CIE_L, CIE_a, CIE_b):
    '''
    Convert from CIE-L*a*b* to XYZ 
    '''

    var_Y = ( CIE_L + 16. ) / 116.
    var_X = CIE_a / 500. + var_Y
    var_Z = var_Y - CIE_b / 200.

    if var_Y**3 > 0.008856: var_Y **= 3.
    else: var_Y = ( var_Y - 16. / 116. ) / 7.787

    if var_X**3 > 0.008856: var_X **= 3.
    else: var_X = ( var_X - 16. / 116. ) / 7.787

    if var_Z**3 > 0.008856: var_Z **= 3
    else: var_Z = ( var_Z - 16. / 116. ) / 7.787

    X = ref_X * var_X     
    Y = ref_Y * var_Y     
    Z = ref_Z * var_Z     

    return X,Y,Z

#-------------------------------------------------#
def rgb_to_cielab(R, G, B):
    '''
    Convert from RGB to CIE-L*a*b*.
    '''
    X,Y,Z = rgb_to_xyz(R,G,B)
    return xyz_to_cielab(X,Y,Z)

#-------------------------------------------------#
def rgb_to_cielch(R, G, B):
    L,A,B = rgb_to_cielab(R,G,B);
  
    C = math.sqrt(A*A + B*B)
    H = math.atan2(B,A)
    if (H > 0): H = (H / 3.1415926536) * 180
    else: H = 360 - (abs(H) / 3.1415926536) * 180
    return L,C,H

#-------------------------------------------------#
def cielab_to_rgb(CIE_L, CIE_a, CIE_b):
    '''
    Convert from CIE-L*a*b* to RGB.
    '''
    X,Y,Z = cielab_to_xyz(CIE_L, CIE_a, CIE_b)
    return xyz_to_rgb(X,Y,Z)

#-------------------------------------------------#
def rgb_to_hsb(R, G, B):
  '''
  Convert from RGB to HSB/HSL
  '''
  vR = (R / 255.0)
  vG = (G / 255.0)
  vB = (B / 255.0)

  CMax = max(vR, max(vG, vB))      # Max. value of RGB
  CMin = min(vR, min(vG, vB))      # Min. value of RGB
  Delta = CMax - CMin              # Delta RGB value

  L = (CMax + CMin) / 2
  if (Delta == 0):                  # Achromatic
    H = 0
    S = 0

  else:                            # Calculate the chroma...
    if (L > 0.5): S = Delta / (2 - CMax - CMin)
    else: S = Delta / (CMax + CMin);
    
    if (vR == CMax): 
        GB = 0 if (vG < vB) else 6
        H = (vG-vB) / Delta + GB
    elif (vG == CMax): H = (vB-vR) / Delta + 2
    elif (vB == CMax): H = (vR-vG) / Delta + 4

    H = H / 6;
  
  return (H*100), (S*100), (L*100)