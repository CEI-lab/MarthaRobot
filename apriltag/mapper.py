

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import map

class Mapper():
    """
    A class to hold a map and provide information about that map
    """

    def __init__(self):
        # temp hardcoded values - to be moved to config file 
        # or calculated from other config values
        self.CELL_SIZE_X = 50
        self.CELL_SIZE_Y = 50
        self.MIN_X = -64
        self.MIN_Y = 0
        self.MAX_X = 1045
        self.MAX_Y = 669

        self.bodies = map.bodies
        obstacles = ([np.array(body) for body in map.bodies if body not in map.clear])
        self.obstacles = []
        for ob in obstacles:
            lines = self.path2lines(ob)
            self.obstacles.append(lines)
        # print(self.obstacles)
        self.obstacles = np.concatenate(self.obstacles).reshape(-1,4)
        self.tags = np.array([np.array(map.tags[tag]) for tag in map.tags])

        xcount = 23
        ycount = 14

        occupancy = [[[]] * xcount] * ycount

        # for body in self.bodies:

        
        # does not account for diagonal length
        self.RAY_LENGTH = max(
            self.MAX_X - self.MIN_X,
            self.MAX_Y - self.MIN_Y
        )

        self.cell_contents = []

    def checkRaysClear(self,rays):
        # print(self.obstacles)
        intersections = self._check_intersect(rays,self.obstacles)
        return np.logical_not(intersections.any(axis=1))

    def coord2grid(self, points):
        """Convert an array of points to gridcell indexes

        :param points: nx2 array of points to convert
        :type points: np.ndarray
        :return: nx2 array of grid cell indices
        :rtype: np.ndarray
        """        
        gridcells = [points[:,0] / self.CELL_SIZE_X,points[:,1]/ self.CELL_SIZE_Y]
        return gridcells
    

    def path2lines(self, path, closepath = True):
        if closepath and (path[-1]!=path[0]).any():
            path = np.append(path,path[0]).reshape(-1,2)
        lines = []
        for i in range(1,len(path)):
            lines.append(np.array([path[i-1],(path[i])]).reshape(1,4))

        return np.array(lines)
    
    def _onSegment_221(self,p:np.ndarray,q:np.ndarray,r:np.ndarray):
        psize = p.shape[0]
        rsize = r.shape[0]
          
        px = p[:,0][np.newaxis].T
        py = p[:,1][np.newaxis].T
        qx = q[:,0][np.newaxis].T
        qy = q[:,1][np.newaxis].T
        rx = r[:,0][np.newaxis]
        ry = r[:,1][np.newaxis]

        res = ( (rx <= np.maximum(px,qx)) & 
                (rx >= np.minimum(px,qx)) &
                (ry <= np.maximum(py,qy)) & 
                (ry >= np.minimum(py,qy)) 
        )

        # assert res.shape == (psize,rsize), str(res.shape) + " is not equal to " + str((psize,rsize))
        return  res

    def _onSegment_112(self,p:np.ndarray,q:np.ndarray,r:np.ndarray):
        psize = p.shape[0]
        rsize = r.shape[0]
          
        px = p[:,0][np.newaxis]
        py = p[:,1][np.newaxis]
        qx = q[:,0][np.newaxis]
        qy = q[:,1][np.newaxis]
        rx = r[:,0][np.newaxis].T
        ry = r[:,1][np.newaxis].T

        res = ( (rx <= np.maximum(px,qx)) & 
                (rx >= np.minimum(px,qx)) &
                (ry <= np.maximum(py,qy)) & 
                (ry >= np.minimum(py,qy)) 
        )

        # assert res.shape == (psize,rsize), str(res.shape) + " is not equal to " + str((psize,rsize))
        return  res


    def _orientation_112(self,p:np.ndarray,q:np.ndarray,r:np.ndarray)->np.ndarray:
        """Return the orientation of triples of points.  

        1 if p,q,r is clockwise
        0 if p,q,r is collinear
        -1 if p,q,r is counter clockwise

        :param p: nx2 array of points
        :type p: np.ndarray
        :param q: nx2 array of points
        :type q: np.ndarray
        :param r: ox2 array of points
        :type r: mp.ndarray

        :return: mxn array
        :rtype: np.ndarray
        """   

        psize = p.shape[0]
        rsize = r.shape[0]
        
        px = p[:,0][np.newaxis]
        py = p[:,1][np.newaxis]
        qx = q[:,0][np.newaxis]
        qy = q[:,1][np.newaxis]
        rx = r[:,0][np.newaxis].T
        ry = r[:,1][np.newaxis].T
        
        vals = ((qy-py) * (rx-qx)) - ((qx - px) * (ry - qy))
        res = np.divide(vals, np.abs(vals), out=np.zeros_like(vals,dtype=float), where=vals!=0)
        # assert res.shape == (psize,rsize), str(res.shape) + " is not equal to " + str((psize,rsize))
        return  res


    def _orientation_221(self,p:np.ndarray,q:np.ndarray,r:np.ndarray)->np.ndarray:
        """Return the orientation of triples of points.  

        1 if p,q,r is clockwise
        0 if p,q,r is collinear
        -1 if p,q,r is counter clockwise

        :param p: nx2 array of points
        :type p: np.ndarray
        :param q: nx2 array of points
        :type q: np.ndarray
        :param r: ox2 array of points
        :type r: mp.ndarray

        :return: nxm array
        :rtype: np.ndarray
        """   

        psize = p.shape[0]
        rsize = r.shape[0]

        px = p[:,0][np.newaxis].T
        py = p[:,1][np.newaxis].T
        qx = q[:,0][np.newaxis].T
        qy = q[:,1][np.newaxis].T
        rx = r[:,0][np.newaxis]
        ry = r[:,1][np.newaxis]        
        
        vals = ((qy-py) * (rx-qx)) - ((qx - px) * (ry - qy))
        res = np.divide(vals, np.abs(vals), out=np.zeros_like(vals,dtype=float), where=vals!=0)
        # assert res.shape == (psize,rsize), str(res.shape) + " is not equal to " + str((psize,rsize))
        return  res.astype(int)
        
    def getTag(self,point):

        for tagid in map.tags:
            print(point)
            print(map.tags[tagid][0:2])
            if (point[0:2] == map.tags[tagid][0:2]).all() or (point[2:] == map.tags[tagid][0:2]).all():
                return tagid
        return None
    
    def getTagRays(self,point):
        res = np.empty((self.tags.shape[0],4))
        res[:,0:2] = point
        res[:,2:] = self.tags[:,0:2]
        return res
    def getTagRays(self,point,center:float,fov):
        res = np.empty((self.tags.shape[0],4))
        res[:,0:2] = point
        res[:,2:] = self.tags[:,0:2]
        angles = np.arctan2((res[:,3]-res[:,1]),(res[:,2]-res[:,0]))
        print(angles)
        minangle = center+fov[0]
        print(minangle)
        maxangle = center+fov[1]
        print(maxangle)
        center = np.angle(center)
        todelete = []
        for i in range(len(angles)):
            a = angles[i]
            if a < (minangle) or a > (maxangle):
                todelete.append(i)
        print(todelete)
        res = np.delete(res,todelete,axis=0)
        
        return res
    def _check_intersect(self,lines1,lines2):
        """Find all intersections between two sets of lines.  Intersections between two lines in the same set will not be reported.

        :param lines1: nx4 array of lines in the form [x1,y1,x2,y2]
        :type lines1: np.ndarray
        :param lines2: mx4 array of lines in the form [xy,y1,x2,y2]
        :type lines2: np.ndarray

        :return: nxm boolean array representing if each line from n intersects with the corresponding line in m.
        :rtype: np.ndarray  
        """
        n = lines1.shape[0]
        m = lines2.shape[1]

        p1 = lines1[:,0:2]
        q1 = lines1[:,2:]
        p2 = lines2[:,0:2]
        q2 = lines2[:,2:]

        o1 = self._orientation_112(p1,q1,p2)
        o2 = self._orientation_112(p1,q1,q2)
        o3 = self._orientation_221(p2,q2,p1)
        o4 = self._orientation_221(p2,q2,q1)

        # print(o1)
        # print(o2)
        # print(o3)
        # print(o4)
        # general case
        intersects = ((o1!=o2) & (o3!=o4))
        # print("general case")
        # print(intersects)

        intersects = intersects | ((o1 == 0) & self._onSegment_112(p1, q1, p2))
        intersects = intersects | ((o2 == 0) & self._onSegment_112(p1, q1, q2))
        intersects = intersects | ((o3 == 0) & self._onSegment_221(p2, q2, p1))
        intersects = intersects | ((o4 == 0) & self._onSegment_221(p2, q2, q1))
        # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
        # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
        # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
        # p2 , q2 and q1 are collinear and q1 lies on segment p2q2


        # assert intersects.shape == (n,m), str(intersects.shape) + " is not equal to " + str((n,m))
        return intersects.T


if __name__=="__main__":


    m = Mapper()
    l1 = np.array([
        [0,0,1,0], #_
        [0,0,1,1], #/
        [0,1,1,1], #-
        [0,1,1,0], #\
        [0,0,0,1], #|_
        [1,0,1,1], #_|
    ])
    l2 = np.array([
        [5,5,6,6], #no intersect
        [5,5,5,6], #no intersect
        [5,5,6,5], #no intersect
        [1,0,1,-1], #intersect _ _| \
        [0.5,0,0.5,-1], #intersect _ 
        [0.5,1,0.5,2], #intersect -
    ])
    res = m._check_intersect(l1,l2)
    # assert res = 
    # print(l1, "\nintersect with \n", l2, "\nat l1↓  l2→\n", res)
    

    poi = np.array([300,300])

    # rays = np.array(m.getTagRays([800,300]))
    rays = np.array(m.getTagRays([800,300],0,(-np.pi/8,np.pi/8)))
    
    print(rays)

    print([m.getTag(ray) for ray in rays])    

    print(m.checkRaysClear(rays))

    cage = map.cage
    lines = m.path2lines(cage)
    # print(cage)
    # print(lines)