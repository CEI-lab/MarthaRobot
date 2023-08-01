import math
from os import path
from pprint import pprint
from typing import Sequence
import typing
import cv2
import numpy as np
import matplotlib
import yaml
import sympy as sym
import seaborn as sns


# matplotlib.use("Agg")
from matplotlib import pyplot as plt
from dataclasses import dataclass
from numpy import pi
from adjustText import adjust_text


class Mapper:
    """
    A class to hold a map and provide information about that map
    """

    def __init__(self, mapname: str, confname: str):
        # plt.ion()
        self.world = FrameSystem("world")
        self.robot = FrameSystem("robot")
        self.plotted_poses = []
        with open(mapname, "r") as mapfile, open(confname, "r") as conffile:
            map = yaml.safe_load(mapfile)
            conf = yaml.safe_load(conffile)

            self.cam_frame = Frame(
                "camera",
                self.robot,
                [conf["CAMERA_X"], conf["CAMERA_Y"], conf["CAMERA_Z"]],
                [
                    conf["CAMERA_YAW"],
                    conf["CAMERA_PITCH"],
                    conf["CAMERA_ROLL"] - math.radians(conf["CAMERA_ROLL_OFFSET"]),
                ],
            )
            # print(math.degrees(conf["CAMERA_ROLL"]-math.radians(conf["CAMERA_ROLL_OFFSET"])))

            exteriors = [point for point in map["EXTERIOR"]]
            bodies = [v for body in map["SOLID_BODIES"] for k, v in body.items()]
            ghosts = [v for body in map["TRANSPARENT_BODIES"] for k, v in body.items()]
            tag_dict = map["APRIL_TAGS"]

            self.tags = []
            self.tag_frames = {}
            for tag in tag_dict:
                self.tags.append(
                    [
                        tag["id"],
                        tag["x"],
                        tag["y"],
                        tag["z"],
                        tag["heading"],
                        tag["heading"],
                        tag["pitch"],
                        tag["roll"],
                    ]
                )
                self.tag_frames[tag["id"]] = self.world.newFrame(
                    str(tag["id"]),
                    [-tag["x"], -tag["y"], -tag["z"]],
                    [tag["yaw"], tag["pitch"], tag["roll"]],
                    self.world.root,
                )
            self.tags = np.array(self.tags).reshape((-1, 8))

            self.exteriors = []
            lines = path2lines(exteriors)
            self.exteriors.append(lines)
            self.exteriors = np.concatenate(self.exteriors).reshape(-1, 4)

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
            self.fov = [fov[0] / 180 * np.pi, fov[1] / 180 * np.pi]

            self.p_false_positive = conf["pFalsePositive"]
            self.p_false_negative = conf["pFalseNegative"]
        # print(self.obstacles)
        # print(self.exteriors)

        palette = sns.color_palette("bright", len(self.tags))
        it = 0
        self.c_dict = {}
        for row in range(len(self.tags)):
            id = self.tags[row, 0]
            self.c_dict[id] = palette[it]
            it += 1

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

    def plot_poses(self, fig, poses):
        plt.figure(fig)

        for pose in self.plotted_poses:
            pose.remove()
        self.plotted_poses = []

        pose_l = [str(p[0]) for p in poses]
        pose_x = [float(p[1]) for p in poses]
        pose_y = [float(p[2]) for p in poses]
        pose_t = [float(p[3]) for p in poses]
        pose_f = [float(p[4]) for p in poses]

        quivs = [
            plt.quiver(
                pose_x[i],
                pose_y[i],
                np.cos(pose_t[i]),
                np.sin(pose_t[i]),
                width=0.003,
                scale=50,
                color=self.getColor(pose_f[i]),
                alpha=0.6,
            )
            for i in range(len(poses))
        ]
        self.plotted_poses = quivs

        # scats = [
        #     plt.scatter(
        #         pose_x[i] + 20 * np.cos(pose_t[i]),
        #         pose_y[i] + 20 * np.sin(pose_t[i]),
        #         alpha=0,
        #     )
        #     for i in range(len(poses))
        # ]

        # end_x = [pose_x[i] + 20 * np.cos(pose_t[i]) for i in range(len(poses))]
        # end_y = [pose_y[i] + 20 * np.cos(pose_t[i]) for i in range(len(poses))]

        # texts = [plt.text(pose_x[i],pose_y[i],
        #                  pose_l[i],
        #                   ha='center',
        #                   va='center',
        #                  size=5,
        #                  weight='bold',
        #                   )
        #         for i in range(len(poses))]

        # adjust_text(texts,
        #             end_x,
        #             end_y,
        #             add_objects=scats,
        #             arrowprops=dict(arrowstyle="-", color='grey', lw=0.75, alpha = 0.5, linewidth=0.1))

        # for pose in poses:
        #     label,x,y,heading = pose
        #     print(heading)
        #     x,y,heading = [float(x),float(y),float(heading)]
        #     card = 0 if heading < pi/4 and heading >= -pi/4 else 1 if heading < 3*pi/4 and heading >=pi/4 else 2 if heading >= 3*pi/4 or heading < -3*pi/4 else 3
        #     plt.quiver(x,y,
        #                np.cos(heading),
        #                np.sin(heading),
        #                width=0.002,
        #                scale=38,)
        #     plt.annotate(label,
        #                  (x  if card in [0,2] else x + 20 ,
        #                   y  if card in [1,3] else y + 20),
        #                   ha='center',
        #                   va='center',
        #                  size=5,
        #                  weight='bold',
        #                   )



    def plot_map(self, fig):
        """Plot the map and output to a png file

        :param filename: file to save the plot to without extension
        :type filename: str
        """
        plt.figure(fig)
        # plt.figure(figsize=(10,5), dpi= 600, facecolor='w', edgecolor='k')
        # plt.figure(dpi=300, facecolor="w", edgecolor="k")
        ax = plt.gca()
        ax.clear()
        ax.set_aspect("equal", adjustable="box")

        for body in self.obstacles:
            x = body[[0, 2]]
            y = body[[1, 3]]
            plt.plot(x, y, c=(0, 0, 0))

        for body in self.ghosts:
            x = body[[0, 2]]
            y = body[[1, 3]]
            plt.plot(x, y, c=(0, 0, 1))

        for body in self.exteriors:
            x = body[[0, 2]]
            y = body[[1, 3]]
            plt.plot(x, y, c=(0, 1, 0))

        for tag in self.tags:
            tagid, x, y, z, heading, yaw, pitch, roll = tag
            card = (
                0
                if heading < pi / 4 and heading >= -pi / 4
                else 1
                if heading < 3 * pi / 4 and heading >= pi / 4
                else 2
                if heading >= 3 * pi / 4 or heading < -3 * pi / 4
                else 3
            )
            plt.quiver(
                x,
                y,
                np.cos(heading),
                np.sin(heading),
                width=0.005,
                scale=50,
                color=self.getColor(tagid),
            )
            plt.annotate(
                int(tagid),
                (
                    x + 10 if card in [0, 2] else x + 20,
                    y + 10 if card in [1, 3] else y + 20,
                ),
                ha="center",
                va="center",
                size=5,
                weight="bold",
                color=self.getColor(tagid),
            )

        # plt.show()

    def plot2file(self, out_filename):
        print("writing map to '", out_filename + ".png", "'")

        plt.savefig(out_filename + ".png")

    def getColor(self, key):
        if key in self.c_dict.keys():
            return self.c_dict[key]
        else:
            return (0, 0, 0)

    def coord2grid(self, points):
        """Convert an array of points to gridcell indexes

        :param points: nx2 array of points to convert
        :type points: np.ndarray
        :return: nx2 array of grid cell indices
        :rtype: np.ndarray
        """
        gridcells = [points[:, 0] / self.CELL_SIZE_X, points[:, 1] / self.CELL_SIZE_Y]
        return gridcells

    def getTagByPoint(self, point):
        """Get the tag id of the first tags which is at the coordinates of each point

        :param point: list or tuple containing (x,y) coordinates
        :type point: list, tuple
        :return: id of tag
        :rtype: int
        """
        # print(self.tags)
        # print(point)
        matching = (self.tags[:, 1:3] == point[2:]).all(axis=1) | (
            self.tags[:, 1:3] == point[0:2]
        ).all(axis=1)
        #   self.tags[:,1:3] == point[:2]
        # for tagid in self.tags:
        #     if (point[0:2] == map.tags[tagid][1:3]).all() or (
        #         point[2:] == map.tags[tagid][1:3]
        #     ).all():
        #         return tagid
        # print(matching)
        return self.tags[np.argmax(matching), 0]

    def getTag(self, tagNum):
        idmatch = self.tags[:, 0] == tagNum
        return self.tags[idmatch, :].reshape(1, 8)

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
        ids = np.array([m.getTagByPoint(ray) for ray in rays])
        return [ids[clear], angles[clear], dists[clear]]

    def pTagsGivenPose(self, pose, detection):
        visible_tags, true_angles, true_dists = self.getVisibleTags(pose)
        det_tags, det_angles, det_dists = detection

        plist = []

        for v in range(len(visible_tags)):
            tag, angle, dist = visible_tags[v], true_angles[v], true_dists[v]
            if tag not in det_tags:
                plist.append(self.p_false_negative)
                plist.append(self.p_false_negative)
            else:
                d = det_tags.find(tag)
                dtag, dangle, ddist = det_tags[d], det_tags[d], det_tags[d]
                plist.append(normpdf(dangle[d], angle[v], self.sigma_rs_theta))
                plist.append(normpdf(ddist[d], dist[v], self.sigma_rs_dist))
        for d in range(len(det_tags)):
            # TODO consider scaling false positive/negative probabilities by distance to tag or similar

            tag = det_tags[d]
            if tag not in visible_tags:
                plist.append(self.p_false_positive)
                plist.append(self.p_false_positive)
        return sum(plist) / len(plist)

    def _frame2frame(origin1, orientation1, origin2, orientation2):
        """Return a transformation matrix to convert from frame 1 to frame 2.

        TR = :func:`_frame2frame(origin1,orient1,origin2,orient2)`
        [x2,y2,z2,1].T = TR @ [x1,y1,z1,1].T

        :param origin1: 3x1 Origin of frame 1 in the world frame
        :type origin1: np.ndarray
        :param orientation1: 3x1 Orientation of frame 1 in the world frame.
        :type orientation1: _type_
        :param origin2: _description_
        :type origin2: _type_
        :param orientation2: _description_
        :type orientation2: _type_
        """
        pass

    def world2tag(self, pose, tag):
        return np.array(self.tag_frames[tag].base2frame(pose)).astype(float)

    def tag2world(self, pose, tag):
        return np.array(self.tag_frames[tag].frame2base(pose)).astype(float)

    def robot2cam(self, pose):
        return np.array(self.cam_frame.base2frame(pose)).astype(float)

    def cam2robot(self, pose):
        return np.array(self.cam_frame.frame2base(pose)).astype(float)

    def robot2world(self, pose, robot_pose):
        t = [robot_pose[0], robot_pose[1], 0]
        r = [robot_pose[2], 0, 0]
        _, robot_rti = getTransformationMatrix(t, r)
        return robot_rti @ pose

    def world2robot(self, pose, robot_pose):
        t = [robot_pose[0], robot_pose[1], 0]
        r = [robot_pose[2], 0, 0]
        robot_rt, _ = getTransformationMatrix(t, r)
        return robot_rt @ pose


# robot x -> forward, y -> left, z -> up
# rhodes hall map x -> north, y -> west, z -> up
# points column vectors 4x1 [x, y, z, 1]T
# transformation matrix:
# [
# [r r r t]
# [r r r t]
# [r r r t]
# [0 0 0 1]
# ]
#
# [
# [r r r t]   [x]   [x']
# [r r r t] @ [y] = [y']
# [r r r t]   [z]   [z']
# [0 0 0 1]   [1]   [1]
# ]


def normpdf(x, mean, sd):
    var = float(sd) ** 2
    denom = (2 * math.pi * var) ** 0.5
    num = math.exp(-((float(x) - float(mean)) ** 2) / (2 * var))
    return num / denom


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

    def _onSegment_112(p: np.ndarray, q: np.ndarray, r: np.ndarray):
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

    def _orientation_112(p: np.ndarray, q: np.ndarray, r: np.ndarray) -> np.ndarray:
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

    def _orientation_221(p: np.ndarray, q: np.ndarray, r: np.ndarray) -> np.ndarray:
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


class point:
    def __init__(self, coordinates, frame):
        self.coordinates = coordinates
        self.frame = frame


class FrameSystem:
    def __init__(self, name: str):
        self.name = name
        self.frames = {}
        self.root = self.newFrame("name", [0, 0, 0], [0, 0, 0], "N/A")
        # self.frames = {"world",self.world}

    def getNames(self):
        return self.frames.keys()

    def __getitem__(self, name: str):
        return self.frames[name]

    def __str__(self) -> str:
        return f"[Frame system '{self.name}']"

    def newFrame(
        self, name: str, origin: np.ndarray, orientation: np.ndarray, base=None
    ):
        newf = Frame(name, self, origin, orientation, base)
        self.frames[name] = newf
        return newf

    def __repr__(self) -> str:
        rep = f"Frame System: {self.name}"
        for name, frame in self.frames.items():
            rep += f"\n   {frame}"
        return rep


class Frame:
    def __str__(self):
        return f"[Frame '{self.name}' at {self.origin} in {self.frame_system}]"

    def __repr__(self):
        return f"[Frame '{self.name}' at {self.origin} in {self.frame_system}]"

    def __eq__(self, value):
        if not isinstance(value, Frame):
            return False
        else:
            return self.name == value.name and self.frame_system == value.frame_system

    def base2frame(self, point):
        return self.forward_m @ point

    def frame2base(self, point):
        return self.backward_m @ point

    class InvalidSizeException(Exception):
        def __init__(self, expected, recieved, message=""):
            super().__init__(
                f"Expected {expected} array, but got {recieved}.\n{message}"
            )

    class UnknownBaseFrame(Exception):
        def __init__(self, base, message=""):
            super().__init__(
                f"{base} cannot be used as a base frame because it is not a known frame.\n{message}"
            )

    class InvalidNameException(Exception):
        def __init__(self, name: str):
            super().__init__(
                f"Cannot create frame named {name} because the name is already in use in the frame system."
            )

    def __init__(
        self,
        name: str,
        frames: FrameSystem,
        origin: np.ndarray,
        orientation: np.ndarray,
        base=None,
    ):
        """A coordinate frame that has its origin at :param:`origin` and rotated by :param:`orientation` in the coordinate frame :param:`base`.

        :param name: Name of the new coordinate frame
        :type name: str
        :param frames: The system this frame will belong to
        :type frames: FrameSystem
        :param origin: Origin of this frame in the base frame
        :type origin: np.ndarray
        :param orientation: Rotation in the current frame from the base frame [rz,ry,rx]
        :type orientation: np.ndarray
        :param base: The base this frame is relative to , defaults to None
        :type base: [str,Frame], optional
        :raises Frame.UnknownBaseFrame: If :param:`base` is not a frame or frame name in :param:`frames`
        """
        assert name not in frames.getNames()
        assert (
            len(origin) == 3
        ), f"Tried to create frame with origin of length {len(origin)} instead of 3"
        assert (
            len(orientation) == 3
        ), f"Tried to create frame with orientation of length {len(orientation)} instead of 3"

        self.name = name
        self.origin = np.array(origin)
        # print(f"{self.origin}")
        self.orientation = np.array(orientation)
        self.frame_system = frames
        self.forward_m, self.backward_m = getTransformationMatrix(origin, orientation)

        # self.forward, self.backward = getTransformationMatrix([origin[0],origin[1],origin[2]],[orientation[0],orientation[1],orientation[2]])

        if base is None:
            self.base = frames.root
        else:
            if isinstance(base, Frame):
                self.base = base
            elif isinstance(base, str):
                if base in self.frame_system.getNames():
                    self.base = self.frame_system[base]
                elif base == "N/A":
                    self.base = None
                else:
                    raise Frame.UnknownBaseFrame(
                        base, "(encountered during initialization of a new frame)"
                    )
            else:
                raise Frame.UnknownBaseFrame(
                    base, "(encountered during initialization of a new frame)"
                )


def scaleVectors(p1, p2, new_lengths):
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
    diffs = p2 - p1
    dists = dist(p1, p2)
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


tx, ty, tz = sym.symbols("tx,ty,tz")
rx, ry, rz = sym.symbols("rx,ry,rz")

cos = sym.cos
sin = sym.sin

trans = sym.Matrix(
    [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1],
    ]
)
rotz = sym.Matrix(
    [
        [cos(rz), sin(rz), 0, 0],
        [-sin(rz), cos(rz), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]
)
roty = sym.Matrix(
    [
        [cos(ry), 0, -sin(ry), 0],
        [0, 1, 0, 0],
        [sin(ry), 0, cos(ry), 0],
        [0, 0, 0, 1],
    ]
)
rotx = sym.Matrix(
    [
        [1, 0, 0, 0],
        [0, cos(rx), sin(rx), 0],
        [0, -sin(rx), cos(rx), 0],
        [0, 0, 0, 1],
    ]
)


tr = rotx @ roty @ rotz @ trans

# sym.pprint(tr)


def getTransformationMatrix(t, r):
    """Get a transformation matrix (and its inverse) composed of translation in the fixed frame of :param:`t` followed by rotation :param:`r` in the body frame.

    :note: :param:`r` has the order [rz,ry,rx] since that is the order the rotations are performed.

    :param t: [tx,ty,tz]
    :type t: list
    :param r: [rz,ry,rx]
    :type r: list
    :return: 4x4 Homogenous transformation matrix
    :rtype: np.ndarray
    """

    tx, ty, tz = sym.symbols("tx,ty,tz")
    rx, ry, rz = sym.symbols("rx,ry,rz")

    substitutions = {
        tx: t[0],
        ty: t[1],
        tz: t[2],
        rz: r[0],
        ry: r[1],
        rx: r[2],
    }
    ret = tr.subs(substitutions)

    return np.array(ret), np.array(ret.inv())


if __name__ == "__main__":
    # plt.ion()
    # m = Mapper("marthabot/map/RhodeMap.yaml", "marthabot/map/MapConfiguration.yaml")
    m = Mapper(
        "C:/Users/63nem/Documents/MarthaRobot/marthabot/map/RhodeMap.yaml",
        "C:/Users/63nem/Documents/MarthaRobot/marthabot/map/MapConfiguration.yaml",
    )

    np.set_printoptions(precision=3, suppress=True)

    origin = np.array([0, 0, 0, 1]).reshape(4, 1).astype(float)
    offset = np.array([100, 0, -100, 0]).reshape(4, 1).astype(float)
    p_tag6 = origin + offset
    p_world = m.tag2world(p_tag6, 6)

    m.plot_map([])

    while True:
        input("show first point")
        poses = np.array(
            [
                # ["origin", 0,0,0],
                ["p_world", p_world[0, 0], p_world[1, 0], 0, 0],
            ]
        )
        m.plot_poses(poses)
        input("clear first pose")
        # for qv in m.plotted_poses:
        #     qv.remove()
        # plt.show()
        input("plot second pose")
        poses = np.array(
            [
                ["origin", 0, 0, 0, 0],
                # ["p_world", p_world[0, 0], p_world[1, 0], 0, 0],
            ]
        )

        m.plot_poses(poses)
        input("clear second pose")
        # for qv in m.plotted_poses:
        #     qv.remove()
