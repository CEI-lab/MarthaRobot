

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
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
    [925,0],
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


bodies = [
    exterior,
    bottom_desk,
    cage,
    topright_desk,
    topmiddle_desk,
    middlemiddle_desk,
    middleisland_desk
]



pi = np.pi
cent = 10.795
centz = 14
sh = 10 + centz

6.5

tags = {
    6: [1045, 381.5-cent, sh, pi],
    4: [0+cent, 0, sh, pi/2],
    3: [358, 274+cent, sh, pi],
    7: [1045,40+cent,sh,pi],
    8: [1045, 261.5-cent, sh, pi],
    9: [1045, 161.5-cent, sh, pi],

}

for body in bodies:
    x = body[:,0]
    y = body[:,1]
    plt.plot(x,y)

for tagid in tags:
    x = tags[tagid][0]
    y = tags[tagid][1]
    t = tags[tagid][3]
    plt.quiver(x,y,np.cos(t),np.sin(t))
    plt.annotate(str(tagid),(x,y))

plt.savefig("map.png")


