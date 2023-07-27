"""
scratch script to 
    take an image
    find tags
    report predicted location
"""

import marthabot.utils.realsense_utils as rsu
import dt_apriltags as atag
import numpy as np
from marthabot.map.mapper import Mapper
import cv2
import seaborn as sns

def draw_pose(
    overlay,
    camera_params,
    tag_size,
    pose_r,
    pose_t,
    linescale=2,
    linewidth=5,
    z_sign=1,
    label=None,
):
    opoints = (np.array(
            [
                0,0,0,
                1,0,0,
                0,1,0,
                0,0,-1 * z_sign,
                0,-1 / linescale,0,
            ]
        ).reshape(-1, 1, 3)
        
        * 0.5
        * tag_size
        * linescale
    )


    fx, fy, cx, cy = camera_params

    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

    # rvec, _ = cv2.Rodrigues(pose_r)
    # tvec = pose_t

    dcoeffs = np.zeros(5)

    ipoints, _ = cv2.projectPoints(opoints, pose_r, pose_t, K, dcoeffs)

    ipoints = np.round(ipoints).astype(int)
    ipoints = [tuple(pt) for pt in ipoints.reshape(-1, 2)]

    textsize = max(abs(ipoints[0][0] - ipoints[1][0]),abs(ipoints[0][0] - ipoints[2][0])) / 100

    dist = round(pose_t[2][0])

    cv2.arrowedLine(overlay, ipoints[0], ipoints[1], (0, 0, 255), linewidth)
    cv2.arrowedLine(overlay, ipoints[0], ipoints[2], (0, 255, 0), linewidth)
    cv2.arrowedLine(overlay, ipoints[0], ipoints[3], (255,0,0), linewidth)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(
        overlay,
        " X",
        ipoints[1],
        font,
        textsize,
        (0, 0, 255),
        round(linewidth / 2),
        cv2.LINE_AA,
    )
    cv2.putText(
        overlay,
        " Y",
        ipoints[2],
        font,
        textsize,
        (0, 255, 0),
        round(linewidth / 2),
        cv2.LINE_AA,
    )
    cv2.putText(
        overlay,
        " Z",
        ipoints[3],
        font,
        textsize,
        (255, 0, 0),
        round(linewidth / 2),
        cv2.LINE_AA,
    )
    cv2.putText(
        overlay,
        str(dist),
        ipoints[0],
        font,
        textsize ,
        (255, 0, 0),
        round(linewidth / 2),
        cv2.LINE_AA,
    )
    if label:
        textwidth = (
            cv2.getTextSize(label, font, textsize * 3, round(linewidth / 2))[0][0] / 2
        )
        ori = (round(ipoints[4][0] - textwidth), ipoints[4][1])
        cv2.putText(
            overlay,
            label,
            ori,
            font,
            textsize * 3,
            (50, 255, 50),
            round(linewidth / 2),
            cv2.LINE_AA,
        )

def rt2orientation(rt):
    r13 = rt[0,2]

    r23 = rt[1,2]
    r33 = rt[2,2]

    r11 = rt[0,0]
    r12 = rt[0,1]

    ry = np.rad2deg(np.arcsin(-r13))
    rz = np.rad2deg(np.arctan2(r12,r11))
    rx = np.rad2deg(np.arctan2(r23,r33))
    return (rz,ry,rx)


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

# create detector
detector = atag.Detector(families="tagStandard41h12")

#get pipe
pipe = rsu.get_pipe()

#camera intrinsics
fx, fy, cx, cy = (
    952., 952.,
    # 952., 556.,
    1920.0/2, 1080.0/2.,
    # 1335.5, 1335.5,
    # 1280.0/2, 720.0/2,
    # 942.0,934.0,623.0,331.0
    # 952.0,942.0,632.0,331.0 #output.jpg
    # 632.0,331.0,


)
camera_params = [fx, fy, cx, cy]

ft2m = 0.3048

size = 8
# size = 0.5

# convert outer edge size to tag size
size = size / 9 * 5

size = size * 12 * ft2m

# size = 0.112888

def deg2vec(angle):
    return [np.cos(np.deg2rad(angle)),np.sin(np.deg2rad(angle))]
def vec2deg(vec):
    return np.rad2deg(np.arctan2(vec[0],vec[1]))


np.set_printoptions(precision=3, suppress=True, formatter={'float': '{: 0.3f}'.format})

m = Mapper("marthabot/map/RhodeMap.yaml",
    "marthabot/map/MapConfiguration.yaml")
    
it = 5

while True:
    print("===============================")
    i = (input("Hit enter to run:\n")).split()
    if len(i) == 1:
        if i[0] == "q":
            exit(0)
    if len(i) == 2:
        if i[0] == "fx":
            fx = float(i[1])
        if i[0] == "fy":
            fy = float(i[1])
        if i[0] == "cx":
            cx = float(i[1])
        if i[0] == "cy":
            cy = float(i[1])
        if i[0] == "i":
            it = int(i[1])
        camera_params = [fx, fy, cx, cy]
        print(camera_params)

# TODO clear dict
    obs = {}

    for i in range(it):
        # print("image",i)
        # image = cv2.imread("marthabot/apriltag/pre.png")
        # image = cv2.imread("marthabot/apriltag/post.png")
        # image = cv2.imread("marthabot/apriltag/realsense/14.jpg")

        # image = cv2.imread("output.jpg")
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


        image, _ = rsu.get_frame(pipe)



        results = detector.detect(image,True,camera_params,size)

        # use if drawing color onto image
        image = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)

        # origin = np.array([0,0,100]).reshape((3,1)).astype(float)
        # draw_pose(
        #         image,
        #         camera_params,
        #         tag_size=size,
        #         pose_r=np.eye(3),
        #         pose_t= origin,
        #         linescale=1,
        #         linewidth=7,

        #         z_sign=-1,
        #         label="Camera Frame",
        #     )
        
        # debug = True
        debug = False

        for tag in results:
            if not tag.tag_id in m.tags[:,0]:
                print("===============================")
                print(f"Skipping tag {tag.tag_id} as it is not in the map file")
                continue
            if debug: print("===============================")
            if debug: print("Tag ", tag.tag_id)
            rt = combine_rt(tag.pose_R,tag.pose_t)
            rt = np.linalg.inv(rt)
            # if debug: print("RT: \n", rt)
            # TODO get rid of intermediate heading calcs
            rz,ry,rx = rt2orientation(rt)
            if debug: print("Translation:",round(rt[0,3]),round(rt[1,3]),round(rt[2,3]))
            if debug: print("Orientation:",round(rz),round(ry),round(rx))
            pose = np.array([0.,0.,0.,1.]).reshape((4,1)).astype(float)
            vec = np.array([50,0,0,1]).reshape((4,1)).astype(float)
            # heading = 0
            # obs[tag.tag_id].append([pose[0,0],pose[1,0],pose[2,0],pose[3,0],heading])
            if debug: print("Robot Frame: ", pose.T)
            # print("Robot vec: ", vec.T)
            pose = m.robot2cam(pose)
            vec = m.robot2cam(vec)
            if debug: print("Cam Frame: ", pose.T)
            pose = rt @ pose 
            vec = rt @ vec 
            if debug: print("Tag Frame: ", pose.T)
            pose = m.tag2world(pose,tag.tag_id)
            vec = m.tag2world(vec,tag.tag_id)

            heading = np.arctan2(vec[1,0]-pose[1,0],vec[0,0]-pose[0,0])
            # obs[tag.tag_id].append([pose[0,0],pose[1,0],pose[2,0],pose[3,0],heading])

            heading = np.arctan2(vec[1,0]-pose[1,0],vec[0,0]-pose[0,0])
            if debug: print("World Frame: ", pose.T)
            # print("World vec: ", vec.T)
            print("Tag ", tag.tag_id, pose.T, round(rz), round(ry), round(rx))
            # print("vec ", tag.tag_id, vec.T, heading)
            # pose.extend(deg2vec(rz))
            pose = [p[0] for p in pose]
            pose.append(heading)
            if tag.tag_id in obs:
                obs[tag.tag_id].append([pose[0],pose[1],pose[2],pose[3],heading])
            else:
                obs[tag.tag_id] = [[pose[0],pose[1],pose[2],pose[3],heading]]
            draw_pose(
                image,
                camera_params,
                tag_size=size,
                pose_r=tag.pose_R,
                pose_t=tag.pose_t,
                linescale=1,
                linewidth=2,
                z_sign=-1,
                # label=str(f"[{round(pose[0])},{round(pose[1])},{round(pose[2])}]"),   #include estimated pose
                label=str(tag.tag_id), #just label with tagid
            )
        if len(results) == 0:
            print("No tags detected")

        poses = []
        palette = sns.color_palette(None, len(obs))
        p_i = 0
        c_dict = {}
        for id, ob in obs.items():
            if id not in c_dict.keys():
                c_dict[id] = palette[p_i]
                p_i += 1
            poses.extend([[str(id), ob[p][0],ob[p][1],ob[p][4],id] for p in range(len(ob))])
            # mx  = round(sum([p[0] for p in ob])/len(ob),1)
            # my  = round(sum([p[1] for p in ob])/len(ob),1)
            # mz  = round(sum([p[2] for p in ob])/len(ob),1)
            # mvx = sum([p[3] for p in ob])
            # mvy = sum([p[4] for p in ob])
            # mt = vec2deg([mvx,mvy])
        poses = np.array(poses)

    print(f"saving {image.shape} image to /output.jpg")
    cv2.line(image,
                (0,              round(cy)),
                (image.shape[1], round(cy)),
                color=(255,0,0)
    )
    cv2.line(image,
                (round(cx), 0),
                (round(cx), image.shape[0]),
                color=(255,0,0)
    )
    cv2.imwrite("output.jpg",image)

    print("saving map to /map.png")
    m.plot_map("marthabot/map/map",np.array(poses))

        # print(id, "- World Frame: ",mx,my,mz, " - with yaw: ",mt)