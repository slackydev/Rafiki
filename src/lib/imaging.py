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

 --- List-operations for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
import numpy as np
import cv2
import Image
import time

from . import search
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

#-------------------------------------------------------------------
def get_image_area(box):
    ''' function naming is getting bad, but what ever...
        Returns the image specified by rect `box`, from within the screen target.
    '''
    (x1,y1,x2,y2) = box
    AREA = target_data()
    _x2 = min(AREA['x2'], AREA['x1'] + x2)
    _y2 = min(AREA['y2'], AREA['y1'] + y2)
    img = grabscreen(AREA['x1'] + x1, AREA['y1'] + y1, _x2, _y2)
    return img

#-------------------------------------------------------------------
def filter_sobel(image):
    ''' Use openCV's sobel-algorithm on a PIL image '''
    scale = 1
    delta = 0
    depth = cv2.CV_16S
    
    if isinstance(image, str): 
        img = cv2.imread(image)
    else: 
        img = np.asarray(image)

    img = cv2.GaussianBlur(img,(3,3),0)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    grad_x = cv2.Sobel(gray,depth,1,0,ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)
    grad_y = cv2.Sobel(gray,depth,0,1,ksize=3, scale=scale, delta=delta, borderType=cv2.BORDER_DEFAULT)

    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)

    dst = cv2.add(abs_grad_x,abs_grad_y)

    sobel = Image.fromstring("L", dst.shape[::-1], dst.tostring())
    return sobel.convert('RGB')


#-------------------------------------------------------------------
def filter_canny(image, _min=0, _max=100):
    ''' Use openCV's canny-algorithm on a PIL image '''
    if isinstance(image, str): 
        img = cv2.imread(image)
    else: 
        img = np.asarray(image)

    img = cv2.GaussianBlur(img,(3,3),0)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, _min, _max, apertureSize = 3)

    res = Image.fromstring("L", canny.shape[::-1], canny.tostring())
    return res.convert('RGB')

#-------------------------------------------------------------------
def find_outlines(img, color, tol=10, ctm=2, _min=(0,0), _max=(9999,9999), adpthresh=True):
    ''' Find the rectangle around the contours, by a spesific color '''
    (minx, miny) = _min
    (maxx, maxy) = _max
    (imW, imH) = img.size

    pixels = search.Pixels()
    pixels.set_taget(img)
    pixels.set_mode(ctm)
    pts = pixels.find(color, (0,0,imW, imH), tol)

    filtered = Image.new('RGB', (imW, imH), (0,0,0))
    pix = filtered.load()
    pix2 = img.load()
    for pt in pts:
        pix[pt[0],pt[1]] = pix2[pt[0],pt[1]]

    arr = np.asarray(filtered)
    gray = cv2.cvtColor(arr,cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(gray,(3,3),0)
    if adpthresh==True:
        img = cv2.adaptiveThreshold(img,255,1,1,11,2)

    contours,hierarchy = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    result = []

    for cnt in contours:
        [x,y,w,h] = cv2.boundingRect(cnt)
        if  w>minx and w<maxx:
            if  h>miny and h<maxy:
                result.append((x, y, x+w, y+h))
    return result

#-------------------------------------------------------------------
def find_contours(img, color, tol=10, ctm=2, _min=(0,0), _max=(9999,9999), line=False):
    ''' Extract the contours of the image, by a spesific color '''
    (minx, miny) = _min
    (maxx, maxy) = _max
    (imW, imH) = img.size

    pixels = search.Pixels()
    pixels.set_taget(img)
    pixels.set_mode(ctm)
    pts = pixels.find(color, (0,0,imW, imH), tol)

    if line:
        method = cv2.CHAIN_APPROX_NONE
    else:
        method = cv2.CHAIN_APPROX_SIMPLE

    filtered = Image.new('RGB', (imW, imH), (0,0,0))
    pix = filtered.load()
    pix2 = img.load()
    for pt in pts:
        pix[pt[0],pt[1]] = pix2[pt[0],pt[1]]

    arr = np.asarray(filtered)
    gray = cv2.cvtColor(arr,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(3,3),0)
    thresh = cv2.adaptiveThreshold(blur,255,1,1,11,2)

    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, method)
    result = []
    for cnt in contours:
        [x,y,w,h] = cv2.boundingRect(cnt)
        if  w>minx and w<maxx:
            if  h>miny and h<maxy:
                result.append([(pt[0][0], pt[0][1]) for pt in cnt])

    return result

#-------------------------------------------------------------------
def get_target_pixels(box):
    ''' Get all pixels from the rect `box`, from within our current target '''
    (x1,y1,x2,y2) = box
    if ((x1 <= x2) and (y1 <= y2)):
        img = get_image_area(box)
        return img.getdata()

#-------------------------------------------------------------------
def calc_pix_error(box, wtime):
    ''' Calculate the pixel change/error over time by the given rect `box`. 
        the image is within our current selected target (from the GUI)...
    '''
    error = 0;
    pix1 = get_target_pixels(box)
    time.sleep(wtime);
    pix2 = get_target_pixels(box)
    for i,px in enumerate(pix1):
        if px != pix2[i]:
            error += 1

    return error

#-------------------------------------------------------------------
def avg_pix_error(box, maxtime=0.7, wtime=0.07):
    ''' Caclulate the average change of the image over X time `maxtime`. 
        two images will be extracted from our target each check, and `wtime`
        is the time between each extraction.
        > Can be used to check if the target is "animating"/changing.
    '''
    error = 0
    i = 0
    wmax = time.time() + maxtime
    while time.time() < wmax:
        error += calc_pix_error(box, wtime)
        i += 1

    return error / float(i)

#An alias for the above function...
is_animating = avg_pix_error
