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
from __future__ import division
from operator import itemgetter
import math

class UnionFind:
    """ Union-find data structure. 
        @note: Items must be hashable.
    """
    def __init__(self):
        """ Create a new empty union-find structure """
        self.weights = {}
        self.parents = {}

    def __getitem__(self, obj):
        """ X[item] will return the token object of the set which contains `item` """

        # check for previously unknown object
        if obj not in self.parents:
            self.parents[obj] = obj 
            self.weights[obj] = 1
            return obj 

        # find path of objects leading to the root
        path = [obj]
        root = self.parents[obj]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def union(self, obj1, obj2):
        """ Merges sets containing obj1 and obj2.
        """
        roots = [self[obj1], self[obj2]]
        heavier = max([(self.weights[r],r) for r in roots])[1]
        for r in roots:
            if r != heavier:
                self.weights[heavier] += self.weights[r]
                self.parents[r] = heavier


#-===================================================================-#
class pointtools:
    #----------------------------------------------------------------- 
    @staticmethod
    def flat_to_points(flatlist):
        return [(flatlist[i], flatlist[i+1]) for i in xrange(0, len(flatlist), 2)]

    #----------------------------------------------------------------- 
    @staticmethod
    def unite(list1, list2):
        """ Combine two lists, remove duplicates """
        return list(set(list1) | set(list2)) 

    #----------------------------------------------------------------- 
    @staticmethod
    def reverse(list):
        """ reverse a list (can be pts, of llpts) """
        return list[::-1]

    #-----------------------------------------------------------------  
    @staticmethod    
    def remove_dupes(list, transform=None):
        """ Removes every duplicate in a list of points """
        if transform is None:
            def transform(x): return x

        seen = {}
        result = []
        for item in list:
            marker = transform(item)
            if marker in seen: continue
            seen[marker] = 1
            result.append(item)
        return result

    #----------------------------------------------------------------- 
    @staticmethod
    def mean_pt(pts):
        """ Find the mean of a list of points """
        xmean = 0
        ymean = 0
        for pt in pts:
            xmean += pt[0] 
            ymean += pt[1]
        x, y = xmean/len(pts), ymean/len(pts)
        return int(round(x)), int(round(y))
    
    #-----------------------------------------------------------------   
    @staticmethod
    def split(pts, vertical=True):
        """ Resulting in a 2-dimansinal list of points. X->Y or Y->X
            @vertical = True : [[(1,3),(1,4),(1,9)], [(2,1),(2,3),(2,7)]]
            @vertical = False: [[(3,1),(6,1),(7,1)], [(2,3),(4,3),(8,3)]]
            --- SLOOOOOOOOOOOW!!!! ---
        """ 
        result, temp = [], []
        maxX = sorted(pts, key = lambda x: x[0], reverse=True)[0][0]
        maxY = sorted(pts, key = lambda x: x[1], reverse=True)[0][1]
        if vertical:
            for x in range(maxX+1):
              for y in xrange(maxY+1):
                if (x,y) in pts:
                  co = pts.count((x,y))
                  for i in range(co):
                    temp.append((x,y))
              if temp:
                result.append(temp)
              temp = []

        else:
            for y in range(maxY+1):
              for x in xrange(maxX+1):
                if (x,y) in pts:
                  co = pts.count((x,y))
                  for i in range(co):
                    temp.append((x,y))
              if temp:
                result.append(temp)
              temp = []

        return result

    #----------------------------------------------------------------- 
    @staticmethod
    def group(pts, distance=1):
        """ Group points by max distance, 
            Resulting in a 2-dimansinal list of points.
        """
        grouped = pointtools.group_ex(pts, distx=distance, disty=distance)
        return grouped

    #----------------------------------------------------------------- 
    @staticmethod
    def group_ex(pts, distx=1, disty=1):
        """ Group points by max distance, 
            Resulting in nested lists of points.
        """
        U = UnionFind()
        for (i, o1) in enumerate(pts):
            for j in range(i + 1, len(pts)):
                o2 = pts[j]
                if abs(o1[0] - o2[0]) <= distx and abs(o1[1] - o2[1]) <= disty:
                    U.union(o1, o2)

        sets = {}
        for pt in pts:
            s = sets.get(U[pt], set())
            s.add(pt)
            sets[U[pt]] = s

        return [list(x) for x in sets.values()]

    #----------------------------------------------------------------- 
    @staticmethod
    def rotate(pts, center, dgrs):
        """ rotate a set of points by x degrees """
        rads = math.radians(dgrs)
        cosrad = math.cos(rads)
        sinrad = math.sin(rads)
        cx,cy = center
        for i,pt in enumerate(pts):
            x = int(round(((pt[1] - cy) * sinrad) + \
                          ((pt[0] - cx) * cosrad) + cx))

            y = int(round(((pt[1] - cy) * cosrad) - \
                          ((pt[0] - cx) * sinrad) + cy))

            pts[i] = (x,y)

        return pts
        
    #----------------------------------------------------------------- 
    @staticmethod
    def sort_by_pt(pts, pt):
        """ Sorts a given list of points/pts by distance from a given point 
            The slow way...
        """
        for k,v in enumerate(pts):
          ptx = v[0] - pt[0]
          pty = v[1] - pt[1]
          value = math.sqrt(ptx*ptx + pty*pty)
          pts[k] = [value, v]

        pts = sorted(pts, key=itemgetter(0))
        for k,v in enumerate(pts):
            pts[k] = v[1]

        return pts

    #----------------------------------------------------------------- 
    @staticmethod
    def sort(pts, item=0, reverse=False):
        ''' Sorts the points by X or Y
            Result is reversed if order=True 
        '''
        return sorted(pts, key=lambda x: x[item], reverse=reverse)
     
    #----------------------------------------------------------------- 
    @staticmethod
    def sort_npoints_by_mean(npts, pt):
        ''' Sorts a given list of list of points by distance from a given point '''
        SIMILAR, result = [], []
        for pts in npts:
          value = abs(mean_pt(pts)[0] - pt[0])
          value += abs(mean_pt(pts)[1] - pt[1])
          SIMILAR.append([value, pts])

        SIMILAR = sorted(SIMILAR, key=itemgetter(0))
        for key in SIMILAR: result.append(key[1])
        return result   

    #-----------------------------------------------------------------
    @staticmethod 
    def sort_npoints_by_size(npts, reverse=False):
        """ Sorts a list of list of pts..
            Orders by length of the sub point-lists
        """
        return sorted(npts, key=lambda x: len(x), reverse=reverse)
         
    #-----------------------------------------------------------------
    @staticmethod     
    def bounds(pts):
        """ Given a list of pts, it will create a rectangular box, 
            returning: [X1,Y1, X2,Y2] 
        """
        h = len(pts)

        x1 = pts[0][0]
        y1 = pts[0][1]
        x2 = pts[0][0]
        y2 = pts[0][1]

        if (h > 1):
          for i in xrange(h):
            if x1 > pts[i][0]:
                x1 = pts[i][0]
            else:                   
                if x2 < pts[i][0]:
                    x2 = pts[i][0]

            if y1 > pts[i][1]:
                y1 = pts[i][1]
            else:
                if y2 < pts[i][1]:
                    y2 = pts[i][1]

        return (x1,y1,x2,y2)

    #----------------------------------------------------------------- 
    @staticmethod
    def dimension(pts):
        """ Returns the dimensions of the area covered by a given list of points """
        box = pointtools.bounds(pts)
        width = box[2] - box[0]
        height = box[3] - box[1]
        return width, height
     
    #-----------------------------------------------------------------  
    @staticmethod 
    def area(pts):
        """ Get the total amount of points within a list of points bounds """  
        w,h = pointtools.dimension(pts)
        return w*h
      
    #-----------------------------------------------------------------
    @staticmethod      
    def density(pts):
        """ Returns the density of a list of points """
        return round(len(pts) / pointtools.area(pts), 5)
     
    #-----------------------------------------------------------------
    @staticmethod 
    def remove_pts(pts1, pts2, all=False):
        """ Removes a given list of points. 
            If all=True every point noted will be removed 
        """
        if all:
          for point in pts2:
            pts1 = filter(lambda a: a != point, pts1)
        else:
          for point in pts2:
            if point in pts1: pts1.remove(point)
    	
        return pts1

    #----------------------------------------------------------------- 
    @staticmethod
    def remove_pt(pts, pt, all=False):
        """ Same as above, but taking a single point """  
        if all: pts = filter(lambda a: a != pt, pts)
        elif pt in pts: pts.remove(pt)
        return pts

    #----------------------------------------------------------------- 
    @staticmethod
    def remove_pts_distance(pts, main, _min, _max, algorithm='euclidean'):
        """ Removes the points that don't have a dist between _min/_max from the
            given mainpoint (main). 
            Distance is defined by 'euclidean', 'chebyshev' or 'manhatten'.
        """
        alogs = ['euclidean', 'chebyshev', 'manhatten']
        if not algorithm in alogs:
            raise Exception(ValueError, 'Undefined algorithm: %s' % algorithm)

        if algorithm.lower() == alogs[0]:
            for pt in list(pts):
                lendx = main[0] - pt[0]
                lendy = main[1] - pt[1]
                length = math.sqrt(lendx*lendx + lendy*lendy)
                if (length < _min) or (length > _max):
                    pts.remove(pt)

        elif algorithm.lower() == alogs[1]:
            for pt in list(pts):
                length = max(abs(main[0] - pt[0]), abs(main[1] - pt[1]))
                if (length < _min) or (length > _max):
                    pts.remove(pt)
            
        elif algorithm.lower() == alogs[2]:
            for pt in list(pts):
                length = abs(main[0] - pt[0]) + abs(main[1] - pt[1])
                if (length < _min) or (length > _max):
                    pts.remove(pt)
                    
        return pts
