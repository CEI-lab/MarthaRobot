
from os import path
import os
from cv2 import INTER_CUBIC
import numpy as np
import cv2
import pyrealsense2 as rs

xsize = 1280
ysize = 720

def get_pipe():
    cfg = rs.config()
    # cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    # cfg.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8 , 6)
    # cfg.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8 , 15)
    cfg.enable_stream(rs.stream.color, 1920, 1080, rs.format.bgr8 , 6)
    pipeline = rs.pipeline()
    pipeline_profile = pipeline.start(cfg)
    sensor = pipeline_profile.get_device().first_depth_sensor()
    return pipeline

def get_frame(pipeline):
    frames = pipeline.wait_for_frames()
    # take owner ship of the frame for further processing
    frames.keep()
    # depth = frames.get_depth_frame()
    rgb = frames.get_color_frame()
    # pose = frames.get_pose_data()
    # color_image = cv2.resize(cv2.cvtColor(np.asanyarray(
    #     rgb.get_data()), cv2.COLOR_BGR2GRAY), (3840, 2160), interpolation=INTER_CUBIC)
    color_image = cv2.resize(cv2.cvtColor(np.asanyarray(
        rgb.get_data()), cv2.COLOR_BGR2GRAY), (1920, 1080), interpolation=INTER_CUBIC)
    # color_image = cv2.resize(cv2.cvtColor(np.asanyarray(
    #     rgb.get_data()), cv2.COLOR_BGR2GRAY), (1280, 720), interpolation=INTER_CUBIC)
    
    ts = frames.get_timestamp()
    return color_image, ts

def save_images(target_dir):
    i = 0
    permpath = path.join(target_dir,str(i)+".jpg")

    pipeline = get_pipe()
    files = os.listdir(target_dir)
    files = [str(target_dir + "/" + f) for f in files if os.path.isfile(target_dir+'/'+f)]

    while True:
        input("Press enter to take a picture")
        image,ts = get_frame(pipeline)
        target_path = path.join(target_dir,str(i)+".jpg")
        while target_path in files:
            i += 1
            target_path = path.join(target_dir,str(i)+".jpg")

        print("Saving to '"+target_path+"'")
        cv2.imwrite(target_path,image)
        cv2.imwrite(permpath,image)
        i += 1
