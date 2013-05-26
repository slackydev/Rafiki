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

 --- shape-operations for the Rafiki Macro Library ---
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
import math

#-------------------------------------------------------------------
class Point:
    """A point identified by (x,y) coordinates.
    
    supports: +, -, *, /, str, repr, iter, getitem
    
    length  -- calculate length of vector to point from origin
    distance_to  -- calculate distance between two points
    as_tuple  -- construct tuple (x,y)
    clone  -- construct a duplicate
    integerize  -- convert x & y to integers
    floatize  -- convert x & y to floats
    move_to  -- reset x & y
    slide  -- move (in place) +dx, +dy, as spec'd by point
    slide_xy  -- move (in place) +dx, +dy
    rotate  -- rotate around the origin
    rotate_about  -- rotate around another point
    """
    
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __add__(self, pt):
        """Point(x1+x2, y1+y2)"""
        return Point(self.x+pt[0], self.y+pt[1])
    
    def __sub__(self, pt):
        """Point(x1-x2, y1-y2)"""
        return Point(self.x-pt[0], self.y-pt[1])
    
    def __mul__(self, scalar):
        """Point(x1*x2, y1*y2)"""
        return Point(self.x*scalar, self.y*scalar)
    
    def __div__(self, scalar):
        """Point(x1/x2, y1/y2)"""
        return Point(self.x/scalar, self.y/scalar)
    
    def __str__(self):
        return "(%s, %s)" % (self.x, self.y)
    
    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__, self.x, self.y)
 
    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, i):
        pt = (self.x, self.y)
        return pt[i]

    def length(self):
        return math.sqrt(self.x*self.x + self.y*self.y)
    
    def distance_to(self, p):
        """Calculate the distance between two points."""
        return (self - p).length()
    
    def as_tuple(self):
        """(x, y)"""
        return (self.x, self.y)
    
    def clone(self):
        """Return a full copy of this point."""
        return Point(self.x, self.y)
    
    def integerize(self):
        """Convert co-ordinate values to integers."""
        self.x = int(self.x)
        self.y = int(self.y)
    
    def floatize(self):
        """Convert co-ordinate values to floats."""
        self.x = float(self.x)
        self.y = float(self.y)
    
    def move_to(self, x, y):
        """Reset x & y coordinates."""
        self.x = x
        self.y = y
    
    def slide(self, p):
        """ Move to new (x+dx,y+dy). """
        self.x = self.x + p.x
        self.y = self.y + p.y
    
    def slide_xy(self, dx, dy):
        """ Move to new (x+dx,y+dy). """
        self.x = self.x + dx
        self.y = self.y + dy
    
    def rotate(self, rad):
        """Rotate counter-clockwise by rad radians.
        
        Positive y goes *up,* as in traditional mathematics.
        
        Interestingly, you can use this in y-down computer graphics, if
        you just remember that it turns clockwise, rather than
        counter-clockwise.
        
        The new position is returned as a new Point.
        """
        s, c = [f(rad) for f in (math.sin, math.cos)]
        x, y = (c*self.x - s*self.y, s*self.x + c*self.y)
        return Point(x,y)
    
    def rotate_about(self, p, theta):
        """Rotate counter-clockwise around a point, by theta degrees.
        
        Positive y goes *up,* as in traditional mathematics.
        
        The new position is returned as a new Point.
        """
        result = self.clone()
        result.slide(-p.x, -p.y)
        result.rotate(theta)
        result.slide(p.x, p.y)
        return result

#-------------------------------------------------------------------
class Rect:
    """A rectangle identified by two points.

    The rectangle stores x1, y1, x2, and y2 values.

    Coordinates are based on screen coordinates.

    origin                               y1
       +---> x increases                  |
       |                             x1 --+-- x2
       v                                  |
    y increases                           y2

    set_points  -- reset rectangle coordinates
    contains  -- is a point inside?
    overlaps  -- does a rectangle overlap?
    top_left  -- get top-left corner
    bottom_right  -- get bottom-right corner
    expanded_by  -- grow (or shrink)
    """

    def __init__(self, pt1, pt2):
        """Initialize a rectangle from two points."""
        self.set_points(pt1, pt2)

    def __str__( self ):
        return "<Rect (%s,%s),(%s,%s)>" % (self.x1, self.y1,
            self.x2, self.y2)
    
    def __repr__(self):
        return "%s(%r, %r)" % (self.__class__.__name__,
            Point(self.x1, self.y1),
            Point(self.x2, self.y2))

    def __iter__(self):
        return iter((self.x1, self.y1, self.x2, self.y2))

    def __getitem__(self, i):
        rect = (self.x1, self.y1, self.x2, self.y2)
        return rect[i]

    def set_points(self, pt1, pt2):
        """Reset the rectangle coordinates."""
        self.x1 = min(pt1[0], pt2[0])
        self.y1 = min(pt1[1], pt2[1])
        self.x2 = max(pt1[0], pt2[0])
        self.y2 = max(pt1[1], pt2[1])

    def contains(self, pt):
        """Return true if a point is inside the rectangle."""
        x,y = pt.as_tuple()
        return (self.x1 <= x <= self.x2 and
                self.y1 <= y <= self.y2)

    def overlaps(self, other):
        """Return true if a rectangle overlaps this rectangle."""
        return (self.x2 > other[0] and self.x1 < other[2] and
                self.y1 < other[3] and self.y2 > other[1])
    
    def top_left(self):
        """Return the top-left corner as a Point."""
        return Point(self.x1, self.y1)
    
    def bottom_right(self):
        """Return the bottom-right corner as a Point."""
        return Point(self.x2, self.y2)
    
    def expanded_by(self, n):
        """Return a rectangle with extended borders.

        Create a new rectangle that is wider and taller than the
        immediate one. All sides are extended by "n" points.
        """
        p1 = Point(self.x1-n, self.y1-n)
        p2 = Point(self.x2+n, self.y2+n)
        return Rect(p1, p2)


''' <Hit tests> / <Check if `pt` is within the bounds of shape `y`> '''
#-------------------------------------------------------------------
def point_in_poly(pt,poly):
    ''' Check if a point is withon a polygon by the given points (poly) '''
    x,y = pt
    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

#-------------------------------------------------------------------
def point_in_circle(pt, center, radius):
    ''' Check if a point is withon circle by the given radius, 
        and center-position.
    '''
    dx = center[0] - pt[0]
    dy = center[1] - pt[1]
    return dx*dx + dy*dy < radius * radius

#-------------------------------------------------------------------
def point_in_ellipse(pt,center, radx,rady):
    ''' Check if a point is withon ellipse by the given radius, 
        and center-position.
    '''
    x = pt[0] - center[0]
    y = pt[1] - center[1]
    return x*x*rady*rady + y*y*radx*radx < rady*rady*radx*radx

#-------------------------------------------------------------------
def point_in_rect(pt, rect_start, rect_end):
    ''' Check if a point is withon rectangle by the given radius, 
        and center-position. Also found in rect-class!
    '''
    (rx1, ry1) = rect_start
    (rx2, ry2) = rect_end
    (x, y) = pt

    return (rx1 <= x <= rx2 and
            ry1 <= y <= ry2)


#=-=-=-=-=-
''' <just some more shit!> '''
#-------------------------------------------------------------------
def angle_in_sector(a,b,c):
    ''' check if an angle is in range of two other angles. '''
    diff = ((a - b + 180) % 360) - 180
    return abs(diff) <= c;

#-------------------------------------------------------------------
def vector_angle(vr1, vr2):
    ''' Calculate the angle between two vectors. 
        Measures clockwise, and vertical!
    '''
    return math.degrees(math.atan2(-(vr1[1] - vr2[1]), (vr1[0] - vr2[0]))) - 90 % 360

