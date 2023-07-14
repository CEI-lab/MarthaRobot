"""


CEI-LAB, Cornell University 2019
"""
import sys
import threading
import subprocess
from multiprocessing import Lock
from pathlib import Path

import time

from commands.command_interface import CommandInterface

import logging


class SleepTwentySecsCommand(CommandInterface):
    _lock = Lock()

    def sleepTwenty(self, responseStatusCallback, jsonObject):
        """This method will wait for 20 seconds before sending a response.

        :param responseStatusCallback: A callback function has to be passed, that will
                send status of command execution back to the controller. This callback will be passed by the
                caller of execute().
        :type responseStatusCallback: func
        :param jsonObject: A JSON object initially containing the command json, modified to include response information.
        :type jsonObject: dictionary
        """

        try:
            self._lock.acquire()
            begin_time = time.time()
            jsonObject["response"] = "UNKNOWN_ERROR"

            time.sleep(20)
            jsonObject["response"] = "SUCCESS"

            # print("3:{}".format(time.time()-begin_time))
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
            # print("4:{}".format(time.time()-begin_time))
        except:
            logging.error("Error")
        finally:
            self._lock.release()

    def execute(self, responseStatusCallback, jsonObject):
        """Start a thread to sleep twenty seconds before responding.

        :param responseStatusCallback: A callback function has to be passed, that will
                send status of command execution back to the controller. This callback will be passed by the
                caller of execute().
        :type responseStatusCallback: func
        :param jsonObject: A JSON object initially containing the command json, modified to include response information.
        :type jsonObject: dictionary
        """
        t1 = threading.Thread(
            target=self.sleepTwenty,
            args=(
                responseStatusCallback,
                jsonObject,
            ),
        )
        t1.start()
