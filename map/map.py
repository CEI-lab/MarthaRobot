from dataclasses import dataclass
import numpy as np
import matplotlib
matplotlib.use('Agg') #headless/noninteractive so it wont crash when running via ssh
from matplotlib import pyplot as plt


exterior = np.array([
    [0,0],
    [0,49],
    [0,140],
    [0,159],
    [-64,159],
    [-64,359],
    [-44,359],
    [-44,669],
    [13,669],
    [358,669],
    [358,274],
    [371,274],
    [371,594],
    [438,594],
    [438,669],
    [802,669],
    [1045,669],
    [1045,388],
    [1045,0],
    [0,0],
])


display_cabinet = np.array([
    [-64,159],
    [5,159],
    [5,359],
    [-64,359],
    [-64,159],
])
filled_space = np.array([
    [-44,359],
    [5,359],
    [5,405],
    [-44,405],
    [-44,359],
])
bottom_desk = np.array([
    [ 112,0],
    [112,76],
    [840,76],
    [840,0],
    [ 112,0],
])
cage = np.array([
    [925,0],
    [925,295],
    [1045,295],
    [1045,0],
])
topright_desk = np.array([
    [1045,479],
    [973,479],
    [973,661],
    [1045,661],
    [1045,479],
])
topmiddle_desk = np.array([
    [438,597],
    [438,669],
    [802,669],
    [802,597],
    [438,597],
])
middlemiddle_desk = np.array([
    [443,594],
    [371,594],
    [371,260],
    [443,260],
    [443,594],
])
middleisland_desk = np.array([
    [443,260],
    [443,332],
    [625,332],
    [625,412],
    [696,412],
    [696,260],
    [443,260],
])
topleft_cabinet1 = np.array([
    [-44,405],
    [5,405],
    [5,491],
    [-44,491],
    [-44,405],
])
topleft_cabinet2 = np.array([
    [-44,491],
    [5,491],
    [5,577],
    [-44,577],
    [-44,491],
])
topleft_cabinet3 = np.array([
    [-44,577],
    [16,577],
    [16,653],
    [-44,653],
    [-44,577],
])


bodies = [
    exterior,
    bottom_desk,
    cage,
    topright_desk,
    topmiddle_desk,
    middlemiddle_desk,
    middleisland_desk,
    display_cabinet,
    filled_space,
    topleft_cabinet1,
    topleft_cabinet2,
    topleft_cabinet3,
]
"""
    List of bodies that the robot should avoid/cant drive through
"""
clear = [exterior,cage]
"""
    List of bodies that are transparent/do not block line of sight.
    Exterior wall is included so it wont block tags.
"""


pi = np.pi
cent = 10.795
centz = 14
sh = 10 + centz

@dataclass
class Tag():
    id_list = []
    def __init__(self, id:int, x: float, y: float, z: float,theta: float):
        """An object holding relevant information about a tag

        :param id: id number of the april tag
        :type id: int
        :param x: x position in map
        :type x: float
        :param y: y position in map
        :type y: float
        :param z: z height from ground
        :type z: float
        :param theta: orientation of tag in radians
        :type theta: float
        :raises Exception: If a new tag is created with an id that has already been used
        """           
        if id in self.id_list:
            raise Exception("Cannot create tag with an already used id")
        else:
            self.id_list.append(id)

        self._id = id
        self._x = x
        self._y = y
        self._z = z
        self._t = theta

    def get_pose(self):
        """The pose of the tag

        :return: [x,y,z,theta]
        :rtype: np.ndarray
        """        
        return np.array([self._x,self._y,self._z,self._t]).resize((1,4))
    def get_id(self):
        return self._id
    def __str__(self):
        acc = "-\n"
        acc += "  id: " + str(self._id) + "\n"
        acc += "  x: " + str(self._x) + "\n"
        acc += "  y: " + str(self._y)+ "\n"
        acc += "  z: " + str(self._z)+ "\n"
        acc += "  theta: " + str(self._t)
        return acc


tags = {
    3: Tag(3, 358,    274+cent,   sh, pi),
    4: Tag(4, 0+cent, 0,          sh, pi/2),
    6: Tag(6, 1045,   381.5-cent, sh, pi),
    7: Tag(7, 1045,   40+cent,    sh, pi),
    8: Tag(8, 1045,   261.5-cent, sh, pi),
    9: Tag(9, 1045,   161.5-cent, sh, pi),
}
"""
Dictionary containing tag information.  Each key represents the tags number, the values are :class:`Tag` objects. 
"""



xrange = range(
    min([min(body[:,0]) for body in bodies]),
    max([max(body[:,0]) for body in bodies]),
    50
)

yrange = range(
    min([min(body[:,1]) for body in bodies]),
    max([max(body[:,1]) for body in bodies]),
    50
)





# for tag in tags:
#     print(tags[tag])