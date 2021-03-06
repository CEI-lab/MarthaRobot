from pathlib import Path
from multiprocessing import Lock
import sys
import os
import threading
import time
import logging

from picamera import PiCamera
from picamera.array import PiRGBArray
from Configurations import *
from CommandInterface import CommandInterface
import asyncore
import subprocess
import os, signal

"""
Implementation of FetchInternalCameraCaptureCommand that will continously capture and send
image from the internal camera, over SCP (ssh copy) to provided destination.

CEI-LAB, Cornell University 2019
"""

class InternalCameraCommand(CommandInterface):
    streaming = False
    def execute_helper(self, responseStatusCallback, jsonObject):
        """
        This method will be called to capture images from the internal camera
        and send it over SCP (ssh copy) to provided remote IP and remote folder name.
        This is a continous process until it breaks with flag keepSendingImages, set by
        the remote user.

        Inputs:
            responseStatusCallback : A callback function has to be passed, that will
                send status of command execution. This callback will be passed by the
                caller of execute().
            jsonObject : A JSON object containing remote IP and remote folder.

        Outputs:
            None
        """
        try:
            if jsonObject["type"] == "single":
                camera = PiCamera()
                if "width" in jsonObject and "height" in jsonObject:
                    camera.resolution = (jsonObject["width"],jsonObject["height"])
                rawCapture = PiRGBArray(camera)
                time.sleep(0.1)
                camera.capture(rawCapture,format='bgr')
                camera.close()
                image = rawCapture.array
                jsonObject["data"] = image
            if jsonObject["type"] == "continuous-start" and not self.streaming:
                if "port" in jsonObject:
                    port = jsonObject["port"]
                else:
                    port = CONFIGURATIONS["DEFAULT_INCAM_PORT"]
                if "width" in jsonObject and "height" in jsonObject:
                    width = jsonObject["width"]
                    height = jsonObject["height"]
                else:
                    width = 0
                    height = 0
                if "fps" in jsonObject:
                    fps = jsonObject["fps"]
                else:
                    fps = 25
                result = subprocess.run(["v4l2-ctl","--list-devices"], capture_output=True)
                device_list = result.stdout.decode().replace("\t","").split("\n")
                dev = device_list[device_list.index("mmal service 16.1 (platform:bcm2835-v4l2):") + 1]
                self.pid = subprocess.Popen([CONFIGURATIONS["RTSP_COMMAND"], "-Q 1", "-P", str(port), "-W" , str(width), "-H", str(height), "-F", str(fps), dev]).pid
                self.streaming = True
            if jsonObject["type"] == "continuous-stop" and self.streaming:
                os.kill(self.pid, signal.SIGTERM)
                self.streaming = False
        # except:
        #     logging.error('InternalCameraCommand : error')
        finally:
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)

    def execute(self, responseStatusCallback, jsonObject):
        t1 = threading.Thread(target=self.execute_helper, args=(responseStatusCallback, jsonObject,))
        t1.start()