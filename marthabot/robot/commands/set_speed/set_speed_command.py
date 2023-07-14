import sys
import threading
import subprocess
from multiprocessing import Lock
from pathlib import Path

import time
import traceback
import os

import marthabot.configurations.robot_config as config
from commands.set_speed.speed_controller import SpeedController
from commands.command_interface import CommandInterface

import logging

print(__name__)
log = logging.getLogger(__name__)

"""
Implementation of SetSpeedCommand that will set speed for right and left wheels.

CEI-LAB, Cornell University 2019
"""

""" TODO fix this -
    possibly get rid of speed controllers 
    (it works, but doesn't use the simultaneious script,
      and the speed controllers probably aren't needed)
"""
class SetSpeedCommand(CommandInterface):
    _lock = Lock()

    def __init__(self):
        log.debug(f"left wheel serial controller is: {config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID}")
        log.debug(f"right wheel serial controller is: {config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID}")
        dir = os.path.split(__file__)[0]
        self.command = os.path.join(dir,"SmcCmd","SmcCmd")
        script_path = os.path.join(dir,"SetSpeed.sh")
        speed_controller_info = subprocess.check_output([self.command, "-l"]).decode(sys.stdout.encoding)
        log.info("Detecting connected motor controllers", {"overflow":speed_controller_info})


        log.debug(f"Creating set speed script at {script_path}")
        with open(script_path, "w") as f:
            f.write("#bin/bash\n")
            f.write(f"\n{self.command} -d {config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID}  $1 &")
            f.write(f"\n{self.command} -d {config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID} $2 &")
            f.write(f"\n\n#This file was written by:\n#   {__file__}")
            f.write(f"\n#It is meant to make it easier to send commands to both motors (semi) simultaneously")


        try:
            self._motor_left = SpeedController(
                config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID
            )
            self._motor_right = SpeedController(
                config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID
            )
        except Exception as e:
            log.warning("SetSpeedCommand : SpeedController objects not created")
            # log.warning((traceback.format_exc()))
            log.exception(e)

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
if __name__ == "__main__":
    test = SetSpeedCommand()