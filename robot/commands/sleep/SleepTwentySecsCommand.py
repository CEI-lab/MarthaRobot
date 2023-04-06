import sys
import threading
import subprocess
from multiprocessing import Lock
from pathlib import Path

import time

from robot.commands.CommandInterface import CommandInterface

import logging

"""
Implementation of SetSpeedCommand that will set speed for right and left wheels.

CEI-LAB, Cornell University 2019
"""


class SleepTwentySecsCommand(CommandInterface):
    _lock = Lock()

    def sleepTwenty(self, responseStatusCallback, jsonObject):
        """
        This method will be called to set speed for wheels.

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
            logging.error(
                'Error')
        finally:
            self._lock.release()

    def execute(self, responseStatusCallback, jsonObject):
        t1 = threading.Thread(target=self.sleepTwenty, args=(
            responseStatusCallback, jsonObject,))
        t1.start()
