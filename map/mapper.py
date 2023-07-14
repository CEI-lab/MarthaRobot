import math
from os import path
from pprint import pprint
from typing import Sequence
import typing
import cv2
import numpy as np
import matplotlib
import yaml


matplotlib.use("Agg")
from matplotlib import pyplot as plt
import map
from dataclasses import dataclass



class Mapper:
    """
    A class to hold a map and provide information about that map
    """

    def __init__(self, mapname:str, confname:str):
        # temp hardcoded values - to be moved to config file
        # or calculated from other config values
        with open(mapname,'r') as mapfile, open(confname,'r') as conffile:
            map = yaml.safe_load(mapfile)
            conf = yaml.safe_load(conffile)

            self.exterior = map["EXTERIOR"]
            bodies = [ v for body in map["SOLID_BODIES"] for k,v in body.items()]
            ghosts = [v for body in map["TRANSPARENT_BODIES"] for k,v in body.items()]
            tag_dict = map["APRIL_TAGS"]

            self.tags = []
            for tag in tag_dict:
                self.tags.append([tag["id"],tag["x"],tag["y"],tag["z"],tag["theta"]])
            self.tags = np.array(self.tags).reshape((-1,5))
        
            self.obstacles = []
            for body in bodies:
                lines = path2lines(body)
                self.obstacles.append(lines)
            self.obstacles = np.concatenate(self.obstacles).reshape(-1, 4)

            self.ghosts = []
            for body in ghosts:
                lines = path2lines(body)
                self.ghosts.append(lines)
            self.ghosts = np.concatenate(self.ghosts).reshape(-1, 4)

            fov = conf["rsFOV"]
            self.fov = [fov[0]/180*np.pi,fov[1]/180*np.pi]

            self.p_false_positive = conf["pFalsePositive"]
            self.p_false_negative = conf["pFalseNegative"]




        self.CELL_SIZE_X = 50
        self.CELL_SIZE_Y = 50
        self.MIN_X = -64
        self.MIN_Y = 0
        self.MAX_X = 1045
        self.MAX_Y = 669

        xcount = 23
        ycount = 14

        # does not account for diagonal length
        self.RAY_LENGTH = max(self.MAX_X - self.MIN_X, self.MAX_Y - self.MIN_Y)

        self.cell_contents = []

    def checkLinesClear(self, rays):
        """Check that a set of lines does not intersect with any solid bodies of the map

        :param rays: Lines to check
        :type rays: np.ndarray
        :return: Boolean array representing if each line passed in is clear
        :rtype: np.ndarray
        """        

        intersections = check_intersect(rays, self.obstacles)
        return np.logical_not(intersections.any(axis=1))



    def plot_map(self, out_filename: str):
        """Plot the map and output to a png file

        :param filename: file to save the plot to without extension
        :type filename: str
        """    
        for body in self.bodies:
            x = body[:,0]
            y = body[:,1]
            plt.plot(x,y)

        for tagid in self.tags:
            x = self.tags[tagid][0]
            y = self.tags[tagid][1]
            t = self.tags[tagid][3]
            plt.quiver(x,y,np.cos(t),np.sin(t))
            plt.annotate(str(tagid),(x,y))

        plt.savefig(out_filename+".png")


    def coord2grid(self, points):
        """Convert an array of points to gridcell indexes

        :param points: nx2 array of points to convert
        :type points: np.ndarray
        :return: nx2 array of grid cell indices
        :rtype: np.ndarray
        """
        gridcells = [points[:, 0] / self.CELL_SIZE_X, points[:, 1] / self.CELL_SIZE_Y]
        return gridcells

    

    def getTag(self, point):
        """Get the tag id of the first tags which is at the coordinates of each point

        :param point: list or tuple containing (x,y) coordinates
        :type point: list, tuple
        :return: id of tag
        :rtype: int
        """
        # print(self.tags)
        # print(point)
        matching = (self.tags[:,1:3] == point[2:]).all(axis=1) | (self.tags[:,1:3] == point[0:2]).all(axis=1)
        #   self.tags[:,1:3] == point[:2]
        # for tagid in self.tags:
        #     if (point[0:2] == map.tags[tagid][1:3]).all() or (
        #         point[2:] == map.tags[tagid][1:3]
        #     ).all():
        #         return tagid
        print(matching)
        return self.tags[np.argmax(matching),0]


    def getTagRays(
        self, point: Sequence[float], center: float = 0, fov=[-np.pi, np.pi]
    ) -> np.ndarray:
        
        res = np.empty((self.tags.shape[0], 4))
        res[:, 0:2] = point
        res[:, 2:] = self.tags[:, 1:3]
        angles = np.arctan2((res[:, 3] - res[:, 1]), (res[:, 2] - res[:, 0]))
        minangle = center + fov[0]
        maxangle = center + fov[1]
        center = np.angle(center)
        todelete = []
        for i in range(len(angles)):
            a = angles[i]
            if a < (minangle) or a > (maxangle):
                todelete.append(i)
        res = np.delete(res, todelete, axis=0)

        return res, angles

    def getVisibleTags(self, pose):
        pos = pose[0:2]
        t = pose[2]
        rays, angles = self.getTagRays(pos, t, self.fov)
        clear = self.checkLinesClear(rays)
        dists = dist(rays[:, :2], rays[:, 2:4])
        ids = np.array([m.getTag(ray) for ray in rays])
        return [ids[clear],angles[clear],dists[clear]]
    
    def pTagsGivenPose(self, pose, detection):
        visible_tags,true_angles,true_dists = self.getVisibleTags(pose)
        det_tags,det_angles,det_dists = detection

        plist = []

        for v in range(len(visible_tags)):
            tag, angle, dist = visible_tags[v],true_angles[v],true_dists[v]
            if tag not in det_tags:
                plist.append(self.p_false_negative)
                plist.append(self.p_false_negative)
            else:
                d = det_tags.find(tag)
                dtag, dangle, ddist = det_tags[d],det_tags[d],det_tags[d]
                plist.append(normpdf(dangle[d],angle[v],self.sigma_rs_theta))
                plist.append(normpdf(ddist[d],dist[v],self.sigma_rs_dist))
        for d in range(len(det_tags)):
            # TODO consider scaling false positive/negative probabilities by distance to tag or similar

            tag = det_tags[d]
            if tag not in visible_tags:
                plist.append(self.p_false_positive)
                plist.append(self.p_false_positive)
        return sum(plist)/len(plist)

def normpdf(x, mean, sd):
    var = float(sd)**2
    denom = (2*math.pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom
    
def check_intersect(lines1, lines2):
    """Check for intersections between two sets of lines.  Intersections between two lines in the same set will not be reported.

    :param lines1: nx4 array of lines in the form [x1,y1,x2,y2]
    :type lines1: np.ndarray
    :param lines2: mx4 array of lines in the form [xy,y1,x2,y2]
    :type lines2: np.ndarray

    :return: nxm boolean array representing if each line from n intersects with the corresponding line in m.
    :rtype: np.ndarray
    """
    
    def _onSegment_221(p: np.ndarray, q: np.ndarray, r: np.ndarray):
        psize = p.shape[0]
        rsize = r.shape[0]

        px = p[:, 0][np.newaxis].T
        py = p[:, 1][np.newaxis].T
        qx = q[:, 0][np.newaxis].T
        qy = q[:, 1][np.newaxis].T
        rx = r[:, 0][np.newaxis]
        ry = r[:, 1][np.newaxis]

        res = (
            (rx <= np.maximum(px, qx))
            & (rx >= np.minimum(px, qx))
            & (ry <= np.maximum(py, qy))
            & (ry >= np.minimum(py, qy))
        )

        # assert res.shape == (psize,rsize), str(res.shape) + " is not equal to " + str((psize,rsize))
        return res

    def _onSegment_112( p: np.ndarray, q: np.ndarray, r: np.ndarray):
        psize = p.shape[0]
        rsize = r.shape[0]

        px = p[:, 0][np.newaxis]
        py = p[:, 1][np.newaxis]
        qx = q[:, 0][np.newaxis]
        qy = q[:, 1][np.newaxis]
        rx = r[:, 0][np.newaxis].T
        ry = r[:, 1][np.newaxis].T

        res = (
            (rx <= np.maximum(px, qx))
            & (rx >= np.minimum(px, qx))
            & (ry <= np.maximum(py, qy))
            & (ry >= np.minimum(py, qy))
        )

        # assert res.shape == (psize,rsize), str(res.shape) + " is not equal to " + str((psize,rsize))
        return res

    def _orientation_112(
         p: np.ndarray, q: np.ndarray, r: np.ndarray
    ) -> np.ndarray:
        """Return the orientation of two points from lines1 and one from lines2

        Identical to :func:`_orientation_221` except return array is shaped differently.

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

        px = p[:, 0][np.newaxis]
        py = p[:, 1][np.newaxis]
        qx = q[:, 0][np.newaxis]
        qy = q[:, 1][np.newaxis]
        rx = r[:, 0][np.newaxis].T
        ry = r[:, 1][np.newaxis].T

        vals = ((qy - py) * (rx - qx)) - ((qx - px) * (ry - qy))
        res = np.divide(
            vals, np.abs(vals), out=np.zeros_like(vals, dtype=float), where=vals != 0
        )
        # assert res.shape == (psize,rsize), str(res.shape) + " is not equal to " + str((psize,rsize))
        return res

    def _orientation_221(
         p: np.ndarray, q: np.ndarray, r: np.ndarray
    ) -> np.ndarray:
        """Return the orientation of two points from lines2 and one from lines1

        Identical to :func:`_orientation_112` except return array is shaped differently.


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

        px = p[:, 0][np.newaxis].T
        py = p[:, 1][np.newaxis].T
        qx = q[:, 0][np.newaxis].T
        qy = q[:, 1][np.newaxis].T
        rx = r[:, 0][np.newaxis]
        ry = r[:, 1][np.newaxis]

        vals = ((qy - py) * (rx - qx)) - ((qx - px) * (ry - qy))
        res = np.divide(
            vals, np.abs(vals), out=np.zeros_like(vals, dtype=float), where=vals != 0
        )
        # assert res.shape == (psize,rsize), str(res.shape) + " is not equal to " + str((psize,rsize))
        return res.astype(int)

    n = lines1.shape[0]
    m = lines2.shape[1]

    p1 = lines1[:, 0:2]
    q1 = lines1[:, 2:]
    p2 = lines2[:, 0:2]
    q2 = lines2[:, 2:]

    o1 = _orientation_112(p1, q1, p2)
    o2 = _orientation_112(p1, q1, q2)
    o3 = _orientation_221(p2, q2, p1)
    o4 = _orientation_221(p2, q2, q1)

    # general case
    intersects = (o1 != o2) & (o3 != o4)

    intersects = intersects | ((o1 == 0) & _onSegment_112(p1, q1, p2))
    intersects = intersects | ((o2 == 0) & _onSegment_112(p1, q1, q2))
    intersects = intersects | ((o3 == 0) & _onSegment_221(p2, q2, p1))
    intersects = intersects | ((o4 == 0) & _onSegment_221(p2, q2, q1))
    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2

    # assert intersects.shape == (n,m), str(intersects.shape) + " is not equal to " + str((n,m))
    return intersects.T

def sweep(pose, angles):
    """ create """
    pass

def scaleVectors(p1,p2,new_lengths):
    """Scale vectors to new lengths, maintining the starting point.

    :param p1: nx2 Starting point [x,y]
    :type p1: np.ndarray
    :param p2: nx2 points to be scaled [x,y]
    :type p2: np.ndarray
    :param new_lengths: Desired lengths of new vectors.  Either nx1, or 1x1
    :type new_lengths: np.ndarray
    :return: Points that combine with :param:`p1` to form the scaled vectors
    :rtype: np.ndarray
    """    
    diffs = p2-p1
    dists = dist(p1,p2)
    return p1 + new_lengths * diffs / dists 
    
def dist(p1, p2):
    """The euclidian distance between `m` dimensional points :param:`p1` and :param:`p2`

    :param p1: nxm array of points
    :type p1:  np.ndarray    
    :param p2: nxm array of points
    :type p2: np.ndarray
    :return: nx1 array of distances
    :rtype: np.ndarray
    """    
    return np.sqrt(np.sum(np.square(p1 - p2), axis=1))

def path2lines(path, closepath=True):
    """Convert an array of points into an array of lines connecting sequential points.

    If :param:`closepath` is True then a line connecting the first and last points will be added unless they are the same point.

    :param path: A list of [n] points
    :type path: list
    :param closepath: If the path should be closed, defaults to True
    :type closepath: bool, optional
    :return: n(+1)x4 array of lines.  Each row is of the form [x1,y1,x2,y2] 
    :rtype: list
    """        
    # print(path)
    if closepath and (path[-1] != path[0]):
        path = np.append(path, path[0]).reshape(-1, 2)
    lines = []
    for i in range(1, len(path)):
        if type(path[i]) == "list":
            lines.extend(path2lines(path[i]))
        else:
            lines.append(np.array([path[i - 1], (path[i])]).reshape(1, 4))

    return lines

if __name__ == "__main__":
    m = Mapper("RhodeMap.yaml","MapConfiguration.yaml")
    l1 = np.array(
        [
            [0, 0, 1, 0],  # _
            [0, 0, 1, 1],  # /
            [0, 1, 1, 1],  # -
            [0, 1, 1, 0],  # \
            [0, 0, 0, 1],  # |_
            [1, 0, 1, 1],  # _|
        ]
    )
    l2 = np.array(
        [
            [5, 5, 6, 6],  # no intersect
            [5, 5, 5, 6],  # no intersect
            [5, 5, 6, 5],  # no intersect
            [1, 0, 1, -1],  # intersect _ _| \
            [0.5, 0, 0.5, -1],  # intersect _
            [0.5, 1, 0.5, 2],  # intersect -
        ]
    )
    res = check_intersect(l1, l2)
    # assert res =
    # print(l1, "\nintersect with \n", l2, "\nat l1↓  l2→\n", res)

    poi = np.array([300, 300])

    # rays = np.array(m.getTagRays([800,300]))
    rays = np.array(m.getTagRays([800, 300], 0, (-np.pi / 8, np.pi / 8)))

    # print(rays)

    # print([m.getTag(ray) for ray in rays])

    # print(m.checkRaysClear(rays))
    # print(rays[:,:2])
    # print(rays[:,2:])
    # print(dist(rays[:,:2],rays[:,2:]))
    res = m.getVisibleTags([800, 300, 0], [-np.pi, np.pi])
    np.set_printoptions(precision=3, suppress=True)
    res.dtype.names = ("tagid","angle","dist")
    print()

    # cage = map.cage
    # lines = path2lines(cage)

    # print(cage)
    # print(lines)