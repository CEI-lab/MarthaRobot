import os
import sys
import threading
from multiprocessing import Lock
from pathlib import Path
import subprocess

from PIL import Image

from Configurations import *
from CommandInterface import CommandInterface

import cv2

"""
Implementation of ProcessProjectImageCommand that will show an image (with or without processing)
given the image is already present in the system.

CEI-LAB, Cornell University 2019
"""


class ImageCommand(CommandInterface):

    def ExecuteHelper(self, responseStatusCallback, jsonObject):
        try:
            if jsonObject["type"] == "list":
                result = subprocess.run(['ls','images'], capture_output=True)
                jsonObject["data"] = result.stdout.decode()
            if jsonObject["type"] == "get" and "name" in jsonObject:
                jsonObject["data"] = cv2.imread("images/{}".format(jsonObject["name"]))
            if jsonObject["type"] == "upload" and "data" in jsonObject and "name" in jsonObject:
                cv2.imwrite("images/{}".format(jsonObject["name"]),jsonObject["data"])
            if jsonObject["type"] == "display" and "data" in jsonObject and "name" not in jsonObject:
                CONFIGURATIONS["DISPLAY_IMAGE"] = jsonObject["data"]
            if jsonObject["type"] == "display" and "name" in jsonObject and "data" not in jsonObject:
                CONFIGURATIONS["DISPLAY_IMAGE"] = cv2.imread("images/{}".format(jsonObject["name"]))
        # except:
        #     logging.error('ImageCommand : unknown error')
        finally:
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
    def execute(self, responseStatusCallback, jsonObject):
        t1 = threading.Thread(target=self.ExecuteHelper, args=(responseStatusCallback, jsonObject,))
        t1.start()

if __name__ == "__main__":
    obj = ProcessProjectImageCommand()
    obj.execute(None, {'cmd': 'ProcessProjectImageCommand', 'imageFileName': 'a.png', 'processImage': True,
                       'projectImage': True, 'priority': 1})
