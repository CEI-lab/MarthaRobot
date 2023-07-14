import sys
import threading
import subprocess
from multiprocessing import Lock
from pathlib import Path

import time
import traceback

import robot.configurations as config
from robot.commands.set_speed.SpeedController import SpeedController
from robot.commands.CommandInterface import CommandInterface

import logging

"""
Implementation of SetSpeedCommand that will set speed for right and left wheels.

CEI-LAB, Cornell University 2019
"""


class SetSpeedCommand(CommandInterface):
    _lock = Lock()

    def __init__(self):
        logging.debug(config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID)
        logging.debug(config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID)
        try:
            self._motor_left = SpeedController(
                config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID
            )
            self._motor_right = SpeedController(
                config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID
            )
        except Exception as e:
            logging.warning("SetSpeedCommand : SpeedController objects not created")
            logging.warning((traceback.format_exc()))

    def _setSpeed(self, responseStatusCallback, jsonObject):
        """This method will be called to set speed for wheels.

        :param responseStatusCallback: A callback function has to be passed, that will
                send status of command execution back to the controller. This callback will be passed by the
                caller of execute().
        :type responseStatusCallback: func
        :param jsonObject: A JSON object initially containing the command json, modified to include response information.
        :type jsonObject: dictionary
        """
        logging.debug("Setting speed")
        try:
            self._lock.acquire()
            begin_time = time.time()
            jsonObject["response"] = "UNKNOWN_ERROR"

            left_speed = jsonObject.get("leftSpeed")
            right_speed = jsonObject.get("rightSpeed")
            # print("1:{}".format(time.time()-begin_time))
            if left_speed is not None and right_speed is not None:
                # logging.info("Running script to set speed commands simultaneously.")
                jsonObject["response"] = "SUCCESS"
                self._motor_left.set_speed(left_speed)
                self._motor_right.set_speed(right_speed)
                # subprocess.call([config.SPEED_CONTROLLER_COMMAND + " -d " +
                #                    config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID  + " " +
                #                        '--speed ' + str(left_speed)])
                # subprocess.call([config.SPEED_CONTROLLER_COMMAND + " -d " +
                #                    config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID  + " " +
                #                        '--speed ' + str(left_speed)])

                # print("current_time is {}".format(time.time()))
                # subprocess.Popen(
                #     [
                #         "sudo",
                #         "/home/pi/HSI/commands/set-speed-command/./SetSpeed.sh",
                #         config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID,
                #         str(left_speed),
                #         config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID,
                #         str(right_speed),
                #     ]
                # )
                # print("2:{}".format(time.time()-begin_time))
            else:
                if left_speed is not None:
                    logging.info(
                        "SetSpeedCommand : Set left speed: " + str(left_speed) + "."
                    )
                    jsonObject["response"] = "SUCCESS"
                    self._motor_left.set_speed(left_speed)
                if right_speed is not None:
                    logging.info(
                        "SetSpeedCommand : Set right speed: " + str(right_speed) + "."
                    )
                    jsonObject["response"] = "SUCCESS"
                    self._motor_right.set_speed(right_speed)
                if left_speed is None and right_speed is None:
                    jsonObject["response"] = "SPEED_VALUES_NOT_PROVIDED"
                    logging.info("SetSpeedCommand : There are no speed values.")

            # print("3:{}".format(time.time()-begin_time))
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
            # print("4:{}".format(time.time()-begin_time))
        except:
            logging.error("SetSpeedCommand : speed controller probably does not exit")
        finally:
            self._lock.release()

    def execute(self, responseStatusCallback, jsonObject):
        t1 = threading.Thread(
            target=self._setSpeed,
            args=(
                responseStatusCallback,
                jsonObject,
            ),
        )
        t1.start()
