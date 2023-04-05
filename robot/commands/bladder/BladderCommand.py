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

import RPi.GPIO as GPIO


import configurations.Configurations as config
import threading
from CommandInterface import CommandInterface


from bladder_motor import bladder_motor as motor_controller


class BladderCommand(CommandInterface):
    _t1 = None
    # _lock = Lock()

    def __init__(self):
        """
        __init__ Create a Bladder Command object.  Takes in commands and performs the appropriate actions.
        """
        GPIO.setmode(GPIO.BCM)

        self.m1Event = threading.Event()
        self.m2Event = threading.Event()
        self.m3Event = threading.Event()

        self.m1 = motor_controller(config.M1_ADDRESS,
                                   config.M1_SELECT,
                                   self.m1Event,
                                   config.ENC1_1_PIN,
                                   config.ENC2_1_PIN)
        self.m2 = motor_controller(config.M2_ADDRESS,
                                   config.M1_SELECT,
                                   self.m2Event,
                                   config.ENC1_2_PIN,
                                   config.ENC2_2_PIN)
        self.m3 = motor_controller(config.M3_ADDRESS,
                                   config.M1_SELECT,
                                   self.m3Event,
                                   config.ENC1_3_PIN,
                                   config.ENC2_3_PIN)

        GPIO.setup(config.FAN_PIN, GPIO.OUT)
        self.fan = GPIO.PWM(config.FAN_PIN, 1000)
        self.fan.start(0)

    def __del__(self):
        """
        __del__ Override built in to disable/stop motors before deleting this object.
        """
        self.m1.motor.disable()
        self.m2.motor.disable()
        self.m3.motor.disable()
        self.fan.stop()

    def stop(self):
        """
        stop Stop all of the motors.
        """
        self.m1.stop()
        self.m2.stop()
        self.m3.stop()

    def move_all(self, direction, speed):
        """
        move_all Move all bladder motors at a specified speed.

        :param direction: Direction to move motors
        :type direction: _type_
        :param speed: Speed to move at.
        :type speed: int
        """
        self.m1.move(direction, speed)
        self.m2.move(direction, speed)
        self.m3.move(direction, speed)

    def move_all_dist(self, dist1, dist2, dist3, direction, speed):
        """
        move_all Move all bladder motors a distance in a specified direction

        :param direction: Direction to move motors
        :type direction: _type_
        :param dist1: Distance to move motor 1
        :type dist1: int
        :param dist2: Distance to move motor 2
        :type dist2: int
        :param dist2: Distance to move motor 3
        :type dist3: int
        """
        self.m1.move_distance(direction, speed, dist1)
        self.m2.move_distance(direction, speed, dist2)
        self.m3.move_distance(direction, speed, dist3)

    def inflate(self):
        """
        inflate Inflate the robot's bladder
        """
        self.fan.ChangeDutyCycle(100)
        time.sleep(10)
        self.m1Event.clear()
        self.m2Event.clear()
        self.m3Event.clear()
        self.move_all_dist(config.BLADDER_SIZE[0],
                           config.BLADDER_SIZE[1],
                           config.BLADDER_SIZE[2],
                           'out',
                           config.BLADDER_SPEED)
        self.m1Event.wait()
        self.m2Event.wait()
        self.m3Event.wait()

    def deflate(self):
        """
        deflate Deflate the robots bladder
        """
        self.fan.ChangeDutyCycle(100)
        self.m1Event.clear()
        self.m2Event.clear()
        self.m3Event.clear()
        self.move_all_dist(config.BLADDER_SIZE[0],
                           config.BLADDER_SIZE[1],
                           config.BLADDER_SIZE[2],
                           'in',
                           config.BLADDER_SPEED)
        self.m1Event.wait()
        self.m2Event.wait()
        self.m3Event.wait()
        self.fan.ChangeDutyCycle(0)

    def _inflate_deflate(self, responseStatusCallback, jsonObject):
        """
        This method will be called to inflate and deflate the air bladder.


        :param responseStatusCallback:  A callback function that will send status of command execution. This callback will be passed by the caller of execute().
        :type direction: function

        :param jsonObject: Command to execute, which will also be used to pass back information as a response.  A dictionary created from a json object.
        :type jsonObject: dictionary

        """
        try:
            jsonObject["response"] = "UNKNOWN_ERROR"
            try:
                if jsonObject["action"] == "inflate":
                    logging.info('Inflating...')
                    self.inflate()
                    logging.info('BladderCommand : Inflate success')
                    jsonObject["response"] = "INFLATE_SUCCESS"
                elif jsonObject["action"] == "deflate":
                    logging.info('Deflating...')
                    self.deflate()
                    logging.info('BladderCommand : Deflate success')
                    jsonObject["response"] = "DEFLATE_SUCCESS"
                else:
                    logging.info('Error...')
                    logging.info(
                        'BladderCommand : There is a typo in the action field.')
                    jsonObject["response"] = "INCORRECT_INFLATE_DEFLATE_FIELD"

            except:
                logging.info('BladderCommand : can\'t open serial port.')
                jsonObject["response"] = "SERIAL_CONNECTION_CLOSED"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            logging.error(
                'BladderCommand : Error probably in responseStatus call or resource is busy')

    def execute(self, responseStatusCallback, jsonObject):
        try:
            jsonObject["response"] = "ACTION_OR_SELECT_FIELD_NOT_IN_JSON"
            if "action" in jsonObject:
                self._t1 = threading.Thread(target=self._inflate_deflate, args=(
                    responseStatusCallback, jsonObject,))
                self._t1.start()
                logging.info('BladderCommand : Process bladder command')
                jsonObject["response"] = "PROCESS_BLADDER_COMMAND"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            logging.error(
                'BladderCommand : Error no action or select field in json object')


if __name__ == "__main__":
    obj = BladderCommand()
    obj.execute(None, {"select": [1, 0, 0], 'action': "inflate"})
