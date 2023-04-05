from pathlib import Path
from multiprocessing import Lock
import sys
import os
import threading
import time
import logging
import pyrealsense2 as rs
import numpy as np
import cv2
from configurations.Configurations import *
from CommandInterface import CommandInterface
import RealSenseServer
import asyncore
"""
Implementation of FetchInternalCameraCaptureCommand that will continously capture and send
image from the internal camera, over SCP (ssh copy) to provided destination.

CEI-LAB, Cornell University 2019
"""


class RealSenseCommand(CommandInterface):
    streaming = False

    def execute_helper(self, responseStatusCallback, jsonObject):
        try:
            if jsonObject["type"] == "single":
                pipeline = rs.pipeline()
                pipeline.start()
                time.sleep(0.1)
                frames = pipeline.wait_for_frames()
                depth = frames.get_depth_frame()
                depth_data = depth.as_frame().get_data()
                np_image = np.asanyarray(depth_data)
                if "colorize" in jsonObject and jsonObject["colorize"] == 1:
                    np_image = cv2.applyColorMap(cv2.convertScaleAbs(
                        np_image, alpha=0.05), cv2.COLORMAP_JET)
                jsonObject["data"] = np_image
            if jsonObject["type"] == "stream":
                self.server = RealSenseServer.RSMulticastServer()
                self.streaming = True
                if responseStatusCallback is not None:
                    responseStatusCallback(jsonObject)
                asyncore.loop()
                print("I am done too.......")
            if jsonObject["type"] == "stop" and self.streaming:
                self.streaming = False
                # asyncore.close()
                self.server.closeServer()
        except:
            logging.error('RealSenseCommand : error in jsonObject')
        finally:
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)

    def execute(self, responseStatusCallback, jsonObject):
        if (jsonObject["type"] == "stream" and self.streaming == False) or jsonObject["type"] == "single" or (jsonObject["type"] == "stop" and self.streaming == True):
            t1 = threading.Thread(target=self.execute_helper, args=(
                responseStatusCallback, jsonObject,))
            t1.start()
