import logging as log
import os
import sys
import threading
from multiprocessing import Lock
from pathlib import Path
import subprocess

import tkinter

from PIL import Image, ImageTk

import robot.configurations as config
from robot.commands.CommandInterface import CommandInterface


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
                result = subprocess.run(['ls', 'images'], capture_output=True)
                jsonObject["data"] = result.stdout.decode()
            if jsonObject["type"] == "get" and "name" in jsonObject:
                jsonObject["data"] = cv2.imread(
                    config.IMAGES_DIRECTORY+jsonObject["name"])
            if jsonObject["type"] == "upload" and "data" in jsonObject and "name" in jsonObject:
                cv2.imwrite(
                    "images/{}".format(jsonObject["name"]), jsonObject["data"])
            if jsonObject["type"] == "display" and "data" in jsonObject and "name" not in jsonObject:
                config.DISPLAY_IMAGE = jsonObject["data"]
            if jsonObject["type"] == "display" and "name" in jsonObject and "data" not in jsonObject:
                config.DISPLAY_IMAGE = cv2.imread(
                    "images/{}".format(jsonObject["name"]))
                log.info("set display image to " + "images/{}".format(jsonObject["name"]))
                config.IMAGES_DIRECTORY+jsonObject["name"]
                try:
                    subprocess.call("pkill feh")
                finally:
                    subprocess.call("feh -F "+config.IMAGES_DIRECTORY+jsonObject["name"]+" &", shell=True)

                # pilImage = Image.open(config.IMAGES_DIRECTORY+jsonObject["name"])
                # root = tkinter.Tk()
                # w, h = root.winfo_screenwidth(), root.winfo_screenheight()
                # root.overrideredirect(1)
                # root.geometry("%dx%d+0+0" % (w, h))
                # root.focus_set()    
                # root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
                # canvas = tkinter.Canvas(root,width=w,height=h)
                # canvas.pack()
                # canvas.configure(background='black')
                # imgWidth, imgHeight = pilImage.size

                # if imgWidth > w or imgHeight > h:
                #     ratio = min(w/imgWidth, h/imgHeight)
                #     imgWidth = int(imgWidth*ratio)
                #     imgHeight = int(imgHeight*ratio)
                #     pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)

                # image = ImageTk.PhotoImage(pilImage)
                # imagesprite = canvas.create_image(w/2,h/2,image=image)
                # root.mainloop()
    
        # except:
        #     logging.error('ImageCommand : unknown error')
        finally:
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)

    def execute(self, responseStatusCallback, jsonObject):
        t1 = threading.Thread(target=self.ExecuteHelper, args=(
            responseStatusCallback, jsonObject,))
        t1.start()


if __name__ == "__main__":
    obj = ProcessProjectImageCommand()
    obj.execute(None, {'cmd': 'ProcessProjectImageCommand', 'imageFileName': 'a.png', 'processImage': True,
                       'projectImage': True, 'priority': 1})
