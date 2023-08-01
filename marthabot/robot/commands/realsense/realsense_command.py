"""
Implementation of FetchInternalCameraCaptureCommand that will continously capture and send
image from the internal camera, over SCP (ssh copy) to provided destination.

CEI-LAB, Cornell University 2019
"""

from pathlib import Path
from multiprocessing import Lock
import sys
import os
import threading
import time
import logging
log = logging.getLogger()
import pyrealsense2 as rs
import numpy as np
import cv2
import marthabot.configurations.robot_config as config
from commands.command_interface import CommandInterface

from marthabot.robot.commands.realsense import realsense_server
import asyncore


class RealSenseCommand(CommandInterface):
    streaming = False

    def execute_helper(self, responseStatusCallback, jsonObject):
        """Handle a realsense command

        :param responseStatusCallback: A callback function has to be passed, that will
                send status of command execution back to the controller. This callback will be passed by the
                caller of execute().
        :type responseStatusCallback: func
        :param jsonObject: A JSON object initially containing the command json, modified to include response information.
        :type jsonObject: dictionary
        """
        try:
            if jsonObject["type"] == "single":
                log.debug("single RS command")
                pipeline = rs.pipeline()
                pipeline.start()
                log.debug("opened and started RS pipleine")
                time.sleep(0.1)
                frames = pipeline.wait_for_frames()
                depth = frames.get_depth_frame()
                depth_data = depth.as_frame().get_data()
                log.debug("Got data")

                np_image = np.asanyarray(depth_data)
                if "colorize" in jsonObject and jsonObject["colorize"] == 1:
                    np_image = cv2.applyColorMap(
                        cv2.convertScaleAbs(np_image, alpha=0.05), cv2.COLORMAP_JET
                    )
                jsonObject["data"] = np_image
            if jsonObject["type"] == "stream":
                self.server = realsense_server.RSMulticastServer()
                self.streaming = True
                if responseStatusCallback is not None:
                    responseStatusCallback(jsonObject)
                asyncore.loop()
                print("I am done too.......")
            if jsonObject["type"] == "stop" and self.streaming:
                self.streaming = False
                # asyncore.close()
                self.server.closeServer()
        except Exception as e:
            log.error("RealSenseCommand : Error")
            log.exception(e)
        finally:
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)

    def execute(self, responseStatusCallback, jsonObject):
        """Entrypoint for realsense command handling

        :param responseStatusCallback: A callback function has to be passed, that will
                send status of command execution back to the controller. This callback will be passed by the
                caller of execute().
        :type responseStatusCallback: func
        :param jsonObject: A JSON object initially containing the command json, modified to include response information.
        :type jsonObject: dictionary
        """
        if (
            (jsonObject["type"] == "stream" and self.streaming == False)
            or jsonObject["type"] == "single"
            or (jsonObject["type"] == "stop" and self.streaming == True)
        ):
            t1 = threading.Thread(
                target=self.execute_helper,
                args=(
                    responseStatusCallback,
                    jsonObject,
                ),
            )
            t1.start()
