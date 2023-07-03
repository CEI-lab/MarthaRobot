
from os import path
import numpy as np
import cv2
import pyrealsense2 as rs


def get_pipe():
    cfg = rs.config()
    cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline = rs.pipeline()
    pipeline_profile = pipeline.start(cfg)
    sensor = pipeline_profile.get_device().first_depth_sensor()
    return pipeline

def get_frame(pipeline):
    frames = pipeline.wait_for_frames()
    # take owner ship of the frame for further processing
    frames.keep()
    depth = frames.get_depth_frame()
    rgb = frames.get_color_frame()
    pose = frames.get_pose_data()
    color_image = cv2.resize(cv2.cvtColor(np.asanyarray(
        rgb.get_data()), cv2.COLOR_BGR2GRAY), (320, 240))
    ts = frames.get_timestamp()
    return color_image, ts

def save_images(target_dir):
    i = 0
    pipeline = get_pipe()
    while True:
        input("Press enter to take a picture")
        image,ts = get_frame(pipeline)
        cv2.imwrite(path.join(target_dir,str(i),".jpg"))
