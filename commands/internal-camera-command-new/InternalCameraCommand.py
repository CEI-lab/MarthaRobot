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
import IntCamServer
import sys
import threading
from multiprocessing import Lock
from pathlib import Path
import cv2
import time

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
            if jsonObject["type"] == "stream" and not self.streaming:
                self.server = IntCamServer.IntCamMulticastServer(jsonObject)
                self.streaming = True
                if responseStatusCallback is not None:
                    responseStatusCallback(jsonObject)
                asyncore.loop()
                print("I am done.......")
            if jsonObject["type"] == "stop" and self.streaming:
                self.streaming = False
                #asyncore.close()
                self.server.closeServer()
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