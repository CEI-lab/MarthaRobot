"""
Command module for controlling the inflatable bladder.

CEI-LAB, Cornell University 2023
"""

from __future__ import print_function
import logging
import sys
import time
from multiprocessing import Lock
from pathlib import Path

try:
    import RPi.GPIO as GPIO
except:
    logging.warning("Could not import RPi.GPIO, importing MOCK module instead")
    from marthabot.robot.mock import MOCK_rpigpio as GPIO


import marthabot.configurations.robot_config as config
import threading
from commands.command_interface import CommandInterface


from marthabot.robot.commands.bladder.bladder_motor import bladder_motor as motor_controller


class BladderCommand(CommandInterface):
    _t1 = None
    # _lock = Lock()

    def __init__(self):
        """
        Create a Bladder Command object.  Takes in commands and performs the appropriate actions.
        """
        GPIO.setmode(GPIO.BCM)

        self.m1Event: threading.Event = threading.Event()
        self.m2Event: threading.Event = threading.Event()
        self.m3Event: threading.Event = threading.Event()

        self.m1: motor_controller = motor_controller(
            config.M1_ADDRESS,
            config.M1_SELECT,
            self.m1Event,
            config.ENC1_1_PIN,
            config.ENC2_1_PIN,
        )
        self.m2: motor_controller = motor_controller(
            config.M2_ADDRESS,
            config.M2_SELECT,
            self.m2Event,
            config.ENC1_2_PIN,
            config.ENC2_2_PIN,
        )
        self.m3: motor_controller = motor_controller(
            config.M3_ADDRESS,
            config.M3_SELECT,
            self.m3Event,
            config.ENC1_3_PIN,
            config.ENC2_3_PIN,
        )

        # logging.debug(self.m1,self.m2,self.m3)
        # Setup and start PWM on the fan pin, with 0 duty cycle
        GPIO.setup(config.FAN_PIN, GPIO.OUT)
        self.fan: GPIO.PWM = GPIO.PWM(config.FAN_PIN, 1000)
        self.fan.start(0)

    def __del__(self):
        """
        Override built in to disable/stop motors before deleting this object.
        """
        self.m1.motor.disable()
        self.m2.motor.disable()
        self.m3.motor.disable()
        self.fan.stop()

    def stop(self):
        """
        Stop all of the bladder motors.  Leaves fan running to keep bladder inflated.
        """
        self.m1.stop()
        self.m2.stop()
        self.m3.stop()

    def move_all(self, direction, speed):
        """
        move_all Move all bladder motors at a specified speed.

        Valid options for direction are ["out",1,"in",0]

        :param direction: Direction to move motors
        :type direction: str, int
        :param speed: Speed to move at.
        :type speed: int
        """
        self.m1.move(direction, speed)
        self.m2.move(direction, speed)
        self.m3.move(direction, speed)

    def move_all_dist(self, dist1, dist2, dist3, direction, speed):
        """
        Move all bladder motors a distance in a specified direction, using :func:`.bladder.bladder_motor.bladder_motor.move_distance`

        Valid options for direction are ["out",1,"in",0]

        :param direction: Direction to move motors
        :type direction: str, int
        :param dist1: Distance to move motor 1
        :type dist1: int
        :param dist2: Distance to move motor 2
        :type dist2: int
        :param dist2: Distance to move motor 3
        :type dist3: int
        """
        # TODO distinct speed per motor, or scale all based on longest dist
        self.m1.move_distance(direction, speed, dist1)
        self.m2.move_distance(direction, speed, dist2)
        self.m3.move_distance(direction, speed, dist3)

    def inflate(self):
        """
        Inflate the robot's bladder completely.  Delays after turning on the fan
        to allow the bladder to inflate before starting to release the pulleys.
        """
        # TODO make sure the encoder based endswitch code is carried over to this file
        self.fan.ChangeDutyCycle(100)
        time.sleep(10)
        self.m1Event.clear()
        self.m2Event.clear()
        self.m3Event.clear()
        self.move_all_dist(
            config.BLADDER_SIZE[0],
            config.BLADDER_SIZE[1],
            config.BLADDER_SIZE[2],
            "out",
            config.BLADDER_SPEED,
        )
        self.m1Event.wait()
        self.m2Event.wait()
        self.m3Event.wait()

    def deflate(self):
        """
        Deflate the robots bladder completely
        """
        self.fan.ChangeDutyCycle(100)
        self.m1Event.clear()
        self.m2Event.clear()
        self.m3Event.clear()
        self.move_all_dist(
            config.BLADDER_SIZE[0],
            config.BLADDER_SIZE[1],
            config.BLADDER_SIZE[2],
            "in",
            config.BLADDER_SPEED,
        )
        self.m1Event.wait()
        self.m2Event.wait()
        self.m3Event.wait()
        self.fan.ChangeDutyCycle(0)

    def _inflate_deflate(self, responseStatusCallback, jsonObject):
        """
        This method will be called to inflate and deflate the air bladder.

        :param responseStatusCallback:  A callback function that will send status of command execution. This callback will be passed by the caller of :meth:`execute`.

        :param jsonObject: Command to execute, which will also be used to pass back information as a response.  A dictionary created from a json object.
        :type jsonObject: dict

        """
        try:
            jsonObject["response"] = "UNKNOWN_ERROR"
            try:
                if jsonObject["action"] == "inflate":
                    logging.info("Inflating...")
                    self.inflate()
                    logging.info("BladderCommand : Inflate success")
                    jsonObject["response"] = "INFLATE_SUCCESS"
                elif jsonObject["action"] == "deflate":
                    logging.info("Deflating...")
                    self.deflate()
                    logging.info("BladderCommand : Deflate success")
                    jsonObject["response"] = "DEFLATE_SUCCESS"
                else:
                    logging.info("Error...")
                    logging.info(
                        "BladderCommand : There is a typo in the action field."
                    )
                    jsonObject["response"] = "INCORRECT_INFLATE_DEFLATE_FIELD"

            except:
                logging.info("BladderCommand : can't open serial port.")
                jsonObject["response"] = "SERIAL_CONNECTION_CLOSED"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            logging.error(
                "BladderCommand : Error probably in responseStatus call or resource is busy"
            )

    def execute(self, responseStatusCallback, jsonObject):
        """Interface entry point to execute a bladder command.  Calls the appropriate helper depending on the command type.

        :param responseStatusCallback: Function to call after execution to send response to computer.

        :param jsonObject: json object representing the command to execute
        :type jsonObject: dict
        """
        try:
            jsonObject["response"] = "ACTION_OR_SELECT_FIELD_NOT_IN_JSON"
            if "action" in jsonObject:
                self._t1 = threading.Thread(
                    target=self._inflate_deflate,
                    args=(
                        responseStatusCallback,
                        jsonObject,
                    ),
                )
                self._t1.start()
                logging.info("BladderCommand : Process bladder command")
                jsonObject["response"] = "PROCESS_BLADDER_COMMAND"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            logging.error(
                "BladderCommand : Error no action or select field in json object"
            )


if __name__ == "__main__":
    obj = BladderCommand()
    obj.execute(None, {"select": [1, 0, 0], "action": "inflate"})