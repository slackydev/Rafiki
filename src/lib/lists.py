#!/usr/bin/python
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
# A set of operations that will focus on lists, and mainly list of points
#
# PS: Division from python v3.x is faster. Hence the __future__ statement
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
from __future__ import division
from operator import itemgetter

class unionFind:
    """ Union-find data structure. 
        Items must be hashable.
    """
    def __init__(self):
        """ Create a new empty union-find structure.
        """
        self.weights = {}
        self.parents = {}

    def __getitem__(self, obj):
        """ X[item] will return the token object of the set which contains `item`
        """

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
class listTools:
    #----------------------------------------------------------------- 
    def flatten(nlist):
        """ flatten one level of nesting """
        return [x for sublist in nlist for x in sublist]

    #----------------------------------------------------------------- 
    def unite(l1, l2):
        """ Combine two lists, remove duplicates """
        return list(set(l1) | set(l2)) 

    #----------------------------------------------------------------- 
    def reverse(lst):
        """ reverse a list """
        return lst[::-1]

    #----------------------------------------------------------------- 
    def mean_pt(pts):
        """ Find the Mean of a list """
        xmean = 0
        ymean = 0
        for pt in pts:
            xmean += pt[0] 
            ymean += pt[1]
        x, y = xmean/len(pts), ymean/len(pts)
        return (x,y)
    
    #-----------------------------------------------------------------     
    def breakdown_pts(pts, usex=True):
        """ Resulting in a 2-dimansinal list. X->Y or Y->X
            @usex = True : [[(1,3),(1,4),(1,9)], [(2,1),(2,3),(2,7)]]
            @usex = False: [[(3,1),(6,1),(7,1)], [(2,3),(4,3),(8,3)]]
        """ 
        result, temp = [], []
        maxX = sorted(pts, key = lambda x: x[0], reverse=True)[0][0]
        maxY = sorted(pts, key = lambda x: x[1], reverse=True)[0][1]
        if usex:
            for x in range(maxX+1):
              for y in xrange(maxY+1):
                if (x,y) in pts:
                  temp.append((x,y))
              if temp:
                result.append(temp)
              temp = []

        else:
            for y in range(maxY+1):
              for x in xrange(maxX+1):
                if (x,y) in pts:
                    temp.append((x,y))
              if temp:
                result.append(temp)
              temp = []

        return result

    #----------------------------------------------------------------- 
    def group_pts(pts, distance=1):
        """ Group points by max distance, 
            resulting in a list of lists of points 
        """
        U = unionFind()
        for (i, x) in enumerate(pts):
            for j in xrange(i + 1, len(pts)):
                y = pts[j]
                if max(abs(x[0] - y[0]), abs(x[1] - y[1])) <= distance:
                    U.union(x, y)

        disjSets = {}
        for x in pts:
            s = disjSets.get(U[x], set())
            s.add(x)
            disjSets[U[x]] = s

        return [list(x) for x in disjSets.values()]
        
    #----------------------------------------------------------------- 
    def group_pts_ex(pts, distx=1, disty=1):
        """ Group points by max distance, 
            resulting in a list of lists of points 
        """
        U = unionFind()
        for (i, x) in enumerate(pts):
            for j in range(i + 1, len(pts)):
                y = pts[j]
                if abs(x[0] - y[0]) <= distx and abs(y[1] - x[1]) <= disty:
                    U.union(x, y)

        disjSets = {}
        for x in pts:
            s = disjSets.get(U[x], set())
            s.add(x)
            disjSets[U[x]] = s

        return [list(x) for x in disjSets.values()]

    #----------------------------------------------------------------- 
    def sort_llpts_by_mean(llpts, pt):
        ''' Sorts a given list of list of points by distance from a given point '''
        SIMILAR, result = [], []
        for pts in llpts:
          value = abs(mean_pt(pts)[0] - pt[0])
          value += abs(mean_pt(pts)[1] - pt[1])
          SIMILAR.append([value, pts])

        SIMILAR = sorted(SIMILAR, key=itemgetter(0))
        for key in SIMILAR: result.append(key[1])
        return result    
        
    #----------------------------------------------------------------- 
    def sort_pts_by_pt(pts, pt):
        ''' Sorts a given list of points/pts by distance from a given point '''
        SIMILAR, result = [], []
        for point in pts:
          value = max(map(lambda a,b: abs(a-b), point, pt))
          SIMILAR.append([value, point])

        SIMILAR = sorted(SIMILAR, key=itemgetter(0))
        for key in SIMILAR:
            result.append(key[1])

        return result
        
    #----------------------------------------------------------------- 
    def sort_pts(pts, item=0, order=False):
        ''' Sorts the points by X or Y
            Result is reversed if order=True 
        '''  
        return sorted(pts, key=lambda x: x[item], reverse=order)
          
    #----------------------------------------------------------------- 
    def sort_llpts_by_size(llpts, order=True):
        """ Sorts a list of list of pts..
            Orders by length of the sub point-lists
        """
        return sorted(llpts, key=lambda x: len(x), reverse=order)
         
    #-----------------------------------------------------------------     
    def pts_bounds(pts):
        """ Given a list of pts, it will create a rectangular box, 
            returning: [X1,Y1, X2,Y2] 
        """ 
        x1 = pts[0][0]
        y1 = pts[0][1]
        x2 = pts[0][0]
        y2 = pts[0][1]
        h = len(pts)
        if (h > 1):
          for i in range(h):
            if (x1 > pts[i][0]):
              x1 = pts[i][0]
            else                    
              if (x2 < pts[i][0]):
                x2 = pts[i[0]

            if (y1 > pts[i][1]):
              y1 = pts[i][1]
            else
              if (y2 < pts[i][1]):
                y2 = pts[i][1]

        return (x1,y1,x2,y2)

    #----------------------------------------------------------------- 
    def pts_dimensions(pts):
        ''' Returns the dimensions of the area covered by a given list of points 
        '''
        box = pts_bounds(pts);
        width = box[2] - box[0];
        height = box[3] - box[1];
        return width, height
     
    #-----------------------------------------------------------------   
    def pts_area(pts):
        ''' Get the total amount of points within a list of points bounds '''  
        w,h = pts_dimensions(pts)
        return w*h
        #Edit: return len(pts)??
      
    #-----------------------------------------------------------------      
    def pts_density(pts):
        ''' Returns the density of a list of points '''  
        return round(len(pts) / pts_area(pts), 5)
     
    #-----------------------------------------------------------------      
    def remove_dupes(pts):
        ''' Removes every duplicate in a list of points 
        ''' 
        return list(set(pts))
     
    #----------------------------------------------------------------- 
    def pts_remove_pts(pts, pts2, all=False):
        ''' Removes a given list of points. 
            If all=True every point noted will be removed 
        '''
        for point in pts2:
            if all: pts = filter(lambda a: a != point, pts)
            elif point in pts: pts.remove(point)
    	
        return pts

    #----------------------------------------------------------------- 
    def pts_remove_pt(pts, pt, all=False):
        ''' Same as above, but taking a single point 
        '''  
        if all: pts = filter(lambda a: a != pt, pts)
        elif pt in pts: pts.remove(pt)
        return pts
