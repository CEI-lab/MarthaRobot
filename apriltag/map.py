

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
#only non solid body is the cage

clear = [exterior,cage]

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

def plot_map():
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






