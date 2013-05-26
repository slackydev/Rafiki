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

 --- "Computer Vision"/Searchfunctions for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~''' 
'''
@note to self, try to speed up with cython:
      might just get lucky, and avoid some C-code!
'''

from ctypes import *
from array import array
from PIL import Image
import cv2
import numpy as np
import os, sys

from .display import get_target_rect, grabscreen


#------------------------------------------------------------------------------
def target_data():
    rect = get_target_rect()
    AREA = {
        'x1': rect[0], 
        'y1': rect[1],
        'x2': rect[0] + rect[2], 
        'y2': rect[1] + rect[3]
    }
    return AREA


#------------------------------------------------------------------------------
if sys.platform == "Windows":
    LibName = 'c_helper.dll'
else:
    LibName = 'c_helper.so'

AbsLibPath = os.path.dirname(os.path.abspath(__file__)) + os.sep
crafiki = CDLL(AbsLibPath + 'clib' + os.sep + LibName)


#------------------------------------------------------------------------------
crafiki.find_colors.restype = POINTER(c_int)
crafiki.find_colors.argtypes = [POINTER(c_int),
                                POINTER(c_ubyte),
                                c_int,
                                c_int,
                                c_int,
                                c_int,
                                c_int,
                                c_char_p,
                                c_int]

''' =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= '''
class Pixels(object):
    #-----
    def __init__(self):
        self.colormode = 1
        self.target = None
    
    #--------------------------------------------------------------------------
    def set_mode(self,mode):
        ''' Set a new colormode. '''
        if mode in [0,1,2,3]:
            self.colormode = mode
        else:
            print "Colormode set to default"
            self.colormode = 0

    #--------------------------------------------------------------------------
    def get_mode(self):
        '''# Get Current colormode.'''
        return self.colormode

    #--------------------------------------------------------------------------
    def set_taget(self, target=None):
        ''' Set target to seach in to a valid PIL image or None '''
        self.target = target

    #--------------------------------------------------------------------------
    def get_target(self):
        ''' Get search target '''
        return self.target

    #--------------------------------------------------------------------------
    def get_image(self, box):
        (x1,y1,x2,y2) = box

        if self.target == None:
            AREA = target_data()
            _x2 = min(AREA['x2'], AREA['x1'] + x2)
            _y2 = min(AREA['y2'], AREA['y1'] + y2)
            img = grabscreen(AREA['x1'] + x1, AREA['y1'] + y1, _x2, _y2)
            x2 = _x2 - AREA['x1']
            y2 = _y2 - AREA['y1']
        else:
            img = self.get_target()
            if img.mode != 'RGB': 
                img = img.convert('RGB')
            img = img.crop((x1, y1, x2, y2))

        return img, x2, y2

    #--------------------------------------------------------------------------
    def find(self, color, box, tolerance=1, flat=False):
        ''' find colors in a image that matches `color`param with a given tolerance '''
        (x1,y1,x2,y2) = box
        (img, x2, y2) = self.get_image(box)
        #Image
        im_buff = img.tostring('raw')
        size = img.size[0] * img.size[1]

        #Find color
        color_arr = array('B', color)
        color_ptr = cast(color_arr.buffer_info()[0], POINTER(c_ubyte))

        #Resulting size
        size = (c_int)()

        #C function
        pts = crafiki.find_colors(size, color_ptr, x1, y1, x2, y2,
                                  tolerance, im_buff, self.colormode)
        

        if flat: return pts[:size.value]
        return [(pts[i], pts[i+1]) for i in xrange(0, size.value, 2)]

    #--------------------------------------------------------------------------  
    def find_first(self, color, box, tolerance=1):
        pass

    #--------------------------------------------------------------------------  
    def find_spiral(self, color, box, tolerance=1, flat=False):    
        pass

    #--------------------------------------------------------------------------  
    def find_spiral_first(self, color, box, tolerance=1):    
        pass

    def find_spiral_rgb(self, rgb, box, tol):
        (tol_r, tol_g, tol_b) = tol
        (img, _, _) = self.get_image(box)

        (x1,y1),(x2,y2) = (0,0), (img.size[0]-1, img.size[1]-1)
        sx = sy = dx = 0
        dy = -1
        CX,CY = (x1+x2)/2, (y1+y2)/2

        pix = img.load()
        for i in xrange(max((x2-x1), (y2-y1))**2):
            if (-CX < sx <= CX) and (-CY < sy <= CY):
                rgb2 = pix[CX+sx, CY+sy]
                if abs(rgb[0] - rgb2[0]) <= tol_r and \
                   abs(rgb[1] - rgb2[1]) <= tol_g and \
                   abs(rgb[2] - rgb2[2]) <= tol_b:
                    return box[0]+CX+sx, box[1]+CY+sy
                    
            if sx == sy or (sx < 0 and sx == -sy) or (sx > 0 and sx == 1-sy):
                dx, dy = -dy, dx
            sx, sy = sx+dx, sy+dy



''' =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= '''
class DTM(object):
    #-----
    def __init__(self):
        self.target = None

    #--------------------------------------------------------------------------
    def set_taget(self, target=None):
        ''' Set target to seach in to a valid PIL image or None '''
        self.target = target

    #--------------------------------------------------------------------------
    def get_target(self):
        ''' Get search target '''
        return self.target

    #--------------------------------------------------------------------------
    def get_image(self, box):
        (x1,y1,x2,y2) = box

        if self.target == None:
            AREA = target_data()
            _x2 = min(AREA['x2'], AREA['x1'] + x2)
            _y2 = min(AREA['y2'], AREA['y1'] + y2)
            img = grabscreen(AREA['x1'] + x1, AREA['y1'] + y1, _x2, _y2)
            x2 = _x2 - AREA['x1']
            y2 = _y2 - AREA['y1']
        else:
            img = self.get_target()
            if img.mode != 'RGB': 
                img = img.convert('RGB')
            img = img.crop((x1, y1, x2, y2))

        return img, x2, y2

    #--------------------------------------------------------------------------
    def find(self, sub, box, points, tol, minmatch=-1):
        ''' find the all points in target that matches the given sub image points '''
        (x1,y1,x2,y2) = box
        (img, x2, y2) = self.get_image(box)

        sW, sH = sub.size
        W,H = x2-sW, y2-sH

        if minmatch == -1:
            minmatch = len(points)

        img_pix = img.load()
        sub_pix = sub.load()
        interest = {(x,y):sub_pix[x,y] for x,y in points}

        result = []
        for x in range(W):
            for y in xrange(H):

                i = 0
                for pt in points:
                    r1,g1,b1 = img_pix[x+pt[0],y+pt[1]]
                    r2,g2,b2 = interest.get(pt)

                    if abs(r1 - r2) <= tol and \
                       abs(g1 - g2) <= tol and \
                       abs(b1 - b2) <= tol:
                          i += 1

                if i >= minmatch:
                    result.append((x1+x, y1+y))

        if len(result) == 0:
            return False
        else:
            return result

    #--------------------------------------------------------------------------
    def find_first(self, sub, box, points, tol, minmatch=-1):
        ''' find the first point in target that matches the given sub image points '''
        (x1,y1,x2,y2) = box
        (img, x2, y2) = self.get_image(box)

        sW, sH = sub.size
        W,H = x2-sW, y2-sH

        if minmatch == -1:
            minmatch = len(points)

        img_pix = img.load()
        sub_pix = sub.load()
        interest = {(x,y):sub_pix[x,y] for x,y in points}

        for x in range(W):
            for y in xrange(H):
                i = 0
                for pt in points:
                    r1,g1,b1 = img_pix[x+pt[0],y+pt[1]]
                    r2,g2,b2 = interest.get(pt)

                    if abs(r1 - r2) <= tol and \
                       abs(g1 - g2) <= tol and \
                       abs(b1 - b2) <= tol:
                          i+=1;

                if i >= minmatch:
                    return (x1+x, y1+y)
              
        return False



''' =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= '''
class Image(object):
    #-----
    def __init__(self):
        self.target = None

    #--------------------------------------------------------------------------
    def set_taget(self, target=None):
        ''' Set target to seach in to a valid PIL image or None '''
        self.target = target

    #--------------------------------------------------------------------------
    def get_target(self):
        ''' Get search target '''
        return self.target

    #--------------------------------------------------------------------------
    def get_image(self, box):
        (x1,y1,x2,y2) = box

        if self.target == None:
            AREA = target_data()
            _x2 = min(AREA['x2'], AREA['x1'] + x2)
            _y2 = min(AREA['y2'], AREA['y1'] + y2)
            img = grabscreen(AREA['x1'] + x1, AREA['y1'] + y1, _x2, _y2)
            x2 = _x2 - AREA['x1']
            y2 = _y2 - AREA['y1']
        else:
            img = self.get_target()
            if img.mode != 'RGB': 
                img = img.convert('RGB')
            img = img.crop((x1, y1, x2, y2))

        return img, x2, y2

    #--------------------------------------------------------------------------
    def find(self, sub, box, rithm='CCOEFF', minval=0.9):
        ''' find all image matches '''
        ALGO = {
            'CCOEFF': cv2.TM_CCOEFF_NORMED,
            'CCORR' : cv2.TM_CCORR_NORMED,
            'SQDIFF': cv2.TM_SQDIFF_NORMED
        }    

        img = np.array(self.get_image(box)[0])
        sub = np.array(sub)

        result = cv2.matchTemplate(sub, img, ALGO[rithm])

        match_indices = np.arange(result.size)[(result>minval).flatten()]
        out = np.unravel_index(match_indices,result.shape)
        
        if minval: 
            if result.max() < minval: 
                return False

        sx,sy = box[0:2]
        return [(sx+out[1][i], sy+out[0][i]) for i in xrange(len(out[0]))]

    #--------------------------------------------------------------------------
    def find_first(self, sub, box, rithm='CCOEFF', minval=0.9):
        ''' find first image match '''
        ALGO = {
            'CCOEFF': cv2.TM_CCOEFF_NORMED,
            'CCORR' : cv2.TM_CCORR_NORMED,
            'SQDIFF': cv2.TM_SQDIFF_NORMED
        }    

        img = np.array(self.get_image(box)[0])
        sub = np.array(sub)
        
        result = cv2.matchTemplate(sub, img, ALGO[rithm])
        best_result = result.max()
        y,x = np.unravel_index(best_result, result.shape)
        if minval: 
            if best_result < minval: 
                return False

        return box[0]+x, box[1]+y

    #--------------------------------------------------------------------------
    def find_by_grid(self, sub, box, gridsize, tol, minmatch=-1):
        ''' find the first point in target that matches the given sub image 
            points, which are defined by the grid '''
        def new_grid(gsize, imsize):
            gx, gy = gsize
            w,h = imsize
            spread = (w/gx, h/gy)
            gpts = list()
            for x in range(gx):
                for y in xrange(gy):
                    gpts.append((gx*spread[0], gy*spread[1]))
            return gpts

        (x1,y1,x2,y2) = box
        (img, x2, y2) = self.get_image(box)

        sW, sH = sub.size
        W,H = x2-sW, y2-sH

        if minmatch == -1:
            minmatch = len(points)

        points = new_grid(gridsize, sub.size)
        img_pix = img.load()
        sub_pix = sub.load()
        interest = {(x,y):sub_pix[x,y] for x,y in points}

        for x in range(W):
            for y in xrange(H):
                i = 0
                for pt in points:
                    r1,g1,b1 = img_pix[x+pt[0],y+pt[1]]
                    r2,g2,b2 = interest.get(pt)

                    if abs(r1 - r2) <= tol and \
                       abs(g1 - g2) <= tol and \
                       abs(b1 - b2) <= tol:
                          i+=1;

                if i >= minmatch:
                    return (x1+x, y1+y)
              
        return False