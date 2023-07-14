import os
import sys
import threading
from multiprocessing import Lock
from pathlib import Path
import logging

import marthabot.configurations.robot_config as config
from commands.command_interface import CommandInterface


"""
Implementation of GetImagesNamesCommand that will get all image names in folder home/HSI/Images.

CEI-LAB, Cornell University 2019
"""

"""
TODO combine with image_command
"""
class GetImagesNamesCommand(CommandInterface):
    _lock = Lock()

    def _getNames(self, responseStatusCallback, jsonObject):
        """
        This method will be called to get all image names.

        Inputs:
            responseStatusCallback : A callback function has to be passed, that will
                send status of command execution. This callback will be passed by the
                caller of execute().
            jsonObject : A JSON object containing text.

        Outputs:
            None
        """
        try:
            self._lock.acquire()
            jsonObject["response"] = "UNKNOWN_ERROR"
            files = os.listdir(config.IMAGES_DIRECTORY.format(config.home))
            imageName = [name for name in files]

            if len(imageName) > 0:
                jsonObject["imageNames"] = imageName
                jsonObject["response"] = "SUCCESS"
            else:
                logging.info("There are no images.")
            responseStatusCallback(jsonObject)
        except:
            logging.error(
                'GetImagesNamesCommand : image folder probably does not exit')
        finally:
            self._lock.release()

    def execute(self, responseStatusCallback, jsonObject):
        t1 = threading.Thread(target=self._getNames, args=(
            responseStatusCallback, jsonObject,))
        t1.start()


if __name__ == "__main__":

    obj = GetImagesNamesCommand()

    def callback(names):
        n = names["imageNames"]
        if n is not None:
            [print(i) for i in n]
        else:
            print("no imageName")

    obj._getNames({'cmd': 'GetImagesNamesCommand'}, callback)
