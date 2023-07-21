import os
import dt_apriltags as atag
import cv2
import numpy as np
from marthabot.map.mapper import Mapper

# https://pyimagesearch.com/2020/11/02/apriltag-with-python/

# create detector
detector = atag.Detector(families="tagStandard41h12")


# read in image
dir = "marthabot/apriltag/realsense/"
name = "14.jpg"

image = cv2.imread(os.path.join(dir,name))

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# test images
fx, fy, cx, cy = (
    952., 952., 1920.0/2, 1080.0/2.
)
# fx, fy, cx, cy = (
#     1335.5, 1335.5, 1920.0/2, 1080.0/2.
# )

# from realsense viewer 
# fx, fy, cx, cy = (
#     1335.5, 1335.5, 952., 556.
# )
camera_params = [fx, fy, cx, cy]
k = [[fx,0,cx],[0,fy,cy],[0,0,1]]

predictions = {}
with open("marthabot/apriltag/realsense/poses.csv","r") as f:
    line = f.readline()
    while line:
        split = [w.strip() for w in line.split(",")]
        # name = split[0].split(".")[0]
        filename = split[0]
        pose = np.ones((4,1))
        pose[:3] = np.array([float(s) for s in split[1:]]).reshape(3,1)
        # pose[0] -= 18
        predictions[filename] = pose
        line = f.readline()


def rt2orientation(rt):
    r13 = rt[0,2]

    r23 = rt[1,2]
    r33 = rt[2,2]

    r11 = rt[0,0]
    r12 = rt[0,1]

    ry = np.arcsin(-r13) * 180 / np.pi
    rz = np.arctan2(r12,r11) * 180 / np.pi
    rx = np.arctan2(r23,r33) * 180 / np.pi
    return (rz,ry,rx)

# print(predictions)

ft2m = 0.3048

size = 8
# size = 0.5

# convert outer edge size to tag size
size = size / 9 * 5

size = size *12 * ft2m

# detect apriltag
results = detector.detect(gray, True, camera_params, size)

m = Mapper("marthabot/map/RhodeMap.yaml",
           "marthabot/map/MapConfiguration.yaml")
def combine_rt(r, t):
    """Combine rotation and transformation matrices into one matrix

    :param r: 3x3 rotation matrix
    :type r: np.ndarray
    :param t: 3x1 translation matrix
    :type t: np.ndarray
    :return: 4x4 transformation matrix
    :rtype: np.ndarray
    """
    return np.array(
        [
            [r[0, 0], r[0, 1], r[0, 2], t[0, 0]],
            [r[1, 0], r[1, 1], r[1, 2], t[1, 0]],
            [r[2, 0], r[2, 1], r[2, 2], t[2, 0]],
            [0, 0, 0, 1],
        ]
    )

np.set_printoptions(precision=3, suppress=True, formatter={'float': '{: 0.3f}'.format})

print("Examining image: ",name)
for tag in results:
    if not tag.tag_id in m.tags[:,0]:
        print("===============================")
        print(f"Skipping tag {tag.tag_id} as it is not in the map file")
        continue
    print("===============================")
    print(tag.tag_id)
    rt: np.ndarray = np.linalg.inv(combine_rt(tag.pose_R,tag.pose_t))
    # print("RT: \n", rt)
    rz,ry,rx = rt2orientation(rt)
    print("orientation",rz,ry,rx)
    pose = np.array([0.,0.,0.,1.]).reshape((4,1)).astype(float)
    print("Robot Frame: ", pose.T)
    pose = m.robot2cam(pose)
    print("Cam Frame: ", pose.T)
    pose = rt @ pose 
    print("Tag Frame: ", pose.T)
    pose = m.tag2world(pose,tag.tag_id)
    print("World Frame: ", pose.T)
    print("Actual:      ", predictions[name].T)

    print("Error:       ", (pose-predictions[name]).T)

exit()

# draws heavily from
# https://github.com/swatbotics/apriltag/blob/master/python/calibrate_camera.py
calibration_images = [
    # "testimages/cal1.jpg",
    "testimages/cal2.jpg",
    "testimages/cal3.jpg",
    "testimages/cal4.jpg",
    "testimages/cal5.jpg",
    "testimages/cal6.jpg",
    "testimages/cal7.jpg",
    "testimages/cal8.jpg",
    "testimages/cal9.jpg",
    "testimages/cal10.jpg",
    "testimages/cal11.jpg",
    "testimages/cal12.jpg",
    "testimages/cal13.jpg",
    "testimages/cal14.jpg",
    "testimages/cal15.jpg",
    "testimages/cal16.jpg",
]
calibration_grid = (9, 5)
calibration_sep = (0.25, 0.5)
calibration_size = 0.75
calibration_offset = (
    calibration_sep[0] + calibration_size,
    calibration_sep[1] + calibration_size,
)
pixel_per_tag = 9
pixel_width = calibration_size / pixel_per_tag
tag_count = calibration_grid[0] * calibration_grid[1]
tag_corners = [
    [2 * pixel_width, 2 * pixel_width],
    [2 * pixel_width, 7 * pixel_width],
    [7 * pixel_width, 7 * pixel_width],
    [7 * pixel_width, 2 * pixel_width],
]

truepoints = []
for x in range(calibration_grid[0]):
    for y in range(calibration_grid[1]):
        origin = (x * calibration_offset[0], y * calibration_offset[1])
        for corner in tag_corners:
            truepoints.append([origin[0] + corner[0], origin[1] + corner[1], 0])


xgrid = np.array([p[0] for p in truepoints])
ygrid = np.array([p[1] for p in truepoints])
zgrid = np.array([p[2] for p in truepoints])

opoints = np.dstack((xgrid, ygrid, zgrid)).reshape((-1, 1, 3)).astype(np.float32)


imagesize = None

truepoints = []
ipoints = []

usableImageCount = 0
unusable = []

for filename in calibration_images:
    rgb = cv2.imread(filename)

    if rgb is None:
        print("warning: error opening {}, skipping".format(filename))
        continue

    cursize = (rgb.shape[1], rgb.shape[0])

    if imagesize is None:
        imagesize = cursize
    else:
        assert imagesize == cursize

    print("loaded " + filename + " of size {}x{}".format(*imagesize))

    if len(rgb.shape) == 3:
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    else:
        gray = rgb

    results = detector.detect(gray)
    if len(results) == tag_count:
        usableImageCount += 1
        truepoints.append(opoints)
        foundpoints = []
        for tag in results:
            corners = tag.corners
            for c in corners:
                foundpoints.append([c])

        ipoints.append(foundpoints)
    else:
        print("could not find all apriltags")
        unusable.append(str(len(results)) + "/" + str(tag_count) + " " + filename)


flags = (
    cv2.CALIB_ZERO_TANGENT_DIST
    | cv2.CALIB_FIX_K1
    | cv2.CALIB_FIX_K2
    | cv2.CALIB_FIX_K3
    | cv2.CALIB_FIX_K4
    | cv2.CALIB_FIX_K5
    | cv2.CALIB_FIX_K6
)
truepoints = np.array(truepoints, dtype=np.float32)
# truepoints = truepoints.reshape((-1,1,3)).astype(np.float32)

ipoints = np.array(ipoints, dtype=np.float32)
# ipoints = ipoints.reshape((-1,1,3)).astype(np.float32)

# print(truepoints.shape)
# print(ipoints.shape)

for el in unusable:
    print(el)
print(
    f"Used {usableImageCount}/{len(calibration_images)} images.  See above for list of unusable images."
)

retval, K, dcoeffs, rvecs, tvecs = cv2.calibrateCamera(
    truepoints,
    ipoints,
    imagesize,
    cameraMatrix=None,
    distCoeffs=np.zeros(5),
    flags=flags,
)
fx = K[0, 0]
fy = K[1, 1]
cx = K[0, 2]
cy = K[1, 2]

params = (fx, fy, cx, cy)

print()
print("all units below measured in pixels:")
print("  fx = {}".format(K[0, 0]))
print("  fy = {}".format(K[1, 1]))
print("  cx = {}".format(K[0, 2]))
print("  cy = {}".format(K[1, 2]))
print()
print("pastable into Python:")
print("  fx, fy, cx, cy = {}".format(repr(params)))
print()
