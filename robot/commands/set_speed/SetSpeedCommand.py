import sys
import threading
import subprocess
from multiprocessing import Lock
from pathlib import Path

import time

from configurations.Configurations import *
from SpeedController import SpeedController
from CommandInterface import CommandInterface
import logging

"""
Implementation of SetSpeedCommand that will set speed for right and left wheels.

CEI-LAB, Cornell University 2019
"""


class SetSpeedCommand(CommandInterface):
    _lock = Lock()

    def __init__(self):
        try:
            self._motor_left = SpeedController(
                CONFIGURATIONS.get("LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID"))
            self._motor_right = SpeedController(
                CONFIGURATIONS.get("RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID"))
        except:
            logging.info(
                "SetSpeedCommand : SpeedController objects not created")

    def _setSpeed(self, responseStatusCallback, jsonObject):
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

            left_speed = jsonObject.get("leftSpeed")
            right_speed = jsonObject.get("rightSpeed")
            # print("1:{}".format(time.time()-begin_time))
            if left_speed is not None and right_speed is not None:
                logging.info(
                    "Running script to set speed commands simultaneously.")
                jsonObject["response"] = "SUCCESS"
                # print("current_time is {}".format(time.time()))
                subprocess.Popen(['sudo', '/home/pi/HSI/commands/set-speed-command/./SetSpeed.sh', CONFIGURATIONS.get(
                    "LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID"), str(left_speed), CONFIGURATIONS.get("RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID"), str(right_speed)])
                # print("2:{}".format(time.time()-begin_time))
            else:
                if left_speed is not None:
                    logging.info(
                        "SetSpeedCommand : Set left speed: " + str(left_speed) + ".")
                    jsonObject["response"] = "SUCCESS"
                    self._motor_left.set_speed(left_speed)
                if right_speed is not None:
                    logging.info(
                        "SetSpeedCommand : Set right speed: " + str(right_speed) + ".")
                    jsonObject["response"] = "SUCCESS"
                    self._motor_right.set_speed(right_speed)
                if left_speed is None and right_speed is None:
                    jsonObject["response"] = "SPEED_VALUES_NOT_PROVIDED"
                    logging.info(
                        "SetSpeedCommand : There are no speed values.")

            # print("3:{}".format(time.time()-begin_time))
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
            # print("4:{}".format(time.time()-begin_time))
        except:
            logging.error(
                'SetSpeedCommand : speed controller probably does not exit')
        finally:
            self._lock.release()

    def execute(self, responseStatusCallback, jsonObject):
        t1 = threading.Thread(target=self._setSpeed, args=(
            responseStatusCallback, jsonObject,))
        t1.start()
