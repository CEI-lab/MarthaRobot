import os
import signal
import sys
import threading
from multiprocessing import Lock
from pathlib import Path
import cv2
import time
import marthabot.configurations.robot_config as config 
from marthabot.robot.commands.command_interface import CommandInterface
import subprocess
import logging
log = logging.getLogger()

"""
Implementation of FetchExternalCameraCaptureCommand that will capture an image
from the external camera and send it over SCP (ssh copy) to provided destination.

CEI-LAB, Cornell University 2019
"""


class ExternalCameraCommand(CommandInterface):
    streaming = False

    def execute_helper(self, responseStatusCallback, jsonObject):
        try:
            if jsonObject["type"] == "single":
                camera = cv2.VideoCapture(config.USB_CAM_ID)
                if "width" in jsonObject and "height" in jsonObject:
                    camera.set(cv2.CAP_PROP_FRAME_WIDTH, jsonObject["width"])
                    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, jsonObject["height"])
                time.sleep(0.1)
                ret, frame = camera.read()
                camera.release()
                print('Took a picture!')
                jsonObject["data"] = frame[:, :, ::-1]
            if jsonObject["type"] == "continuous-start" and not self.streaming:
                if "port" in jsonObject:
                    port = jsonObject["port"]
                else:
                    port = config.EXT_CAM_PORT
                if "width" in jsonObject and "height" in jsonObject:
                    width = jsonObject["width"]
                    height = jsonObject["height"]
                else:
                    width = 10
                    height = 10
                if "fps" in jsonObject:
                    fps = jsonObject["fps"]
                else:
                    fps = 25
                self.pid = subprocess.Popen([config.RTSP_COMMAND, "-Q 1", "-P", str(
                    port), "-W", str(width), "-H", str(height), "-F", str(fps), config.USB_CAM_ID]).pid
                self.streaming = True
            if jsonObject["type"] == "continuous-stop" and self.streaming:
                os.kill(self.pid, signal.SIGTERM)
                self.streaming = False
        except:
            log.error('InternalCameraCommand : unknown error')
        finally:
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)

    def execute(self, responseStatusCallback, jsonObject):
        t1 = threading.Thread(target=self.execute_helper, args=(
            responseStatusCallback, jsonObject,))
        t1.start()
