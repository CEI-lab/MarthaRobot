import dt_apriltags as atag
import cv2
import numpy as np

# https://pyimagesearch.com/2020/11/02/apriltag-with-python/

# create detector
detector = atag.Detector(families="tagStandard41h12")


# tag details - main
tagsize = 8

# tag details - calibration sheet
tagsize = 0.5

# camera parameters


# read in image
image = cv2.imread("testimages/tag1.jpg")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


fx, fy, cx, cy = (867.1714530943214, 7.2700778250832485, 518.2694115721059, 910.7793844438535)


# detect apriltag
results = detector.detect(gray,True,[fx,fy,cx,cy],0.2032)

print(results)

# print("[INFO] {} total AprilTags detected".format(len(results)))


# for tag in results:
#     corners = np.array(tag.corners, np.int32)
#     corners = corners.reshape((-1,1,2))
#     cv2.polylines(image,[corners],True,(0,255,0),3)

# cv2.imwrite("output.jpg", image)

exit()



# draws heavily from 
# https://github.com/swatbotics/apriltag/blob/master/python/calibrate_camera.py
calibration_images=[
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
    "testimages/cal16.jpg"
]
calibration_grid = (9,5)
calibration_sep = (0.25,0.5)
calibration_size = 0.75
calibration_offset = (calibration_sep[0]+calibration_size,
                        calibration_sep[1]+calibration_size)
pixel_per_tag = 9
pixel_width = calibration_size / pixel_per_tag
tag_count = calibration_grid[0] * calibration_grid[1]
tag_corners = [
    [2*pixel_width,2*pixel_width],
    [2*pixel_width,7*pixel_width],
    [7*pixel_width,7*pixel_width],
    [7*pixel_width,2*pixel_width]
]

truepoints = []
for x in range(calibration_grid[0]):
    for y in range(calibration_grid[1]):
        origin = (x*calibration_offset[0],y*calibration_offset[1])
        for corner in tag_corners:
            truepoints.append([origin[0]+corner[0],origin[1]+corner[1],0])


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
        print('warning: error opening {}, skipping'.format(filename))
        continue

    cursize = (rgb.shape[1], rgb.shape[0])
    
    if imagesize is None:
        imagesize = cursize
    else:
        assert imagesize == cursize

    print('loaded ' + filename + ' of size {}x{}'.format(*imagesize))

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

        ipoints.append( foundpoints )
    else:
        print("could not find all apriltags")
        unusable.append(str(len(results)) + "/" + str(tag_count) + " " +filename)


flags = (cv2.CALIB_ZERO_TANGENT_DIST |
            cv2.CALIB_FIX_K1 |
            cv2.CALIB_FIX_K2 |
            cv2.CALIB_FIX_K3 |
            cv2.CALIB_FIX_K4 |
            cv2.CALIB_FIX_K5 |
            cv2.CALIB_FIX_K6)
truepoints = np.array(truepoints,dtype=np.float32)
# truepoints = truepoints.reshape((-1,1,3)).astype(np.float32)

ipoints = np.array(ipoints,dtype=np.float32)
# ipoints = ipoints.reshape((-1,1,3)).astype(np.float32)

# print(truepoints.shape)
# print(ipoints.shape)

for el in unusable:
    print(el)
print(f"Used {usableImageCount}/{len(calibration_images)} images.  See above for list of unusable images.")

retval, K, dcoeffs, rvecs, tvecs = cv2.calibrateCamera(
    truepoints,
    ipoints,
    imagesize,
    cameraMatrix=None,
    distCoeffs=np.zeros(5),
    flags=flags)
fx = K[0,0]
fy = K[1,1]
cx = K[0,2]
cy = K[1,2]

params = (fx, fy, cx, cy)

print()
print('all units below measured in pixels:')
print('  fx = {}'.format(K[0,0]))
print('  fy = {}'.format(K[1,1]))
print('  cx = {}'.format(K[0,2]))
print('  cy = {}'.format(K[1,2]))
print()
print('pastable into Python:')
print('  fx, fy, cx, cy = {}'.format(repr(params)))
print()


