"""
Command module for controlling the inflatable bladder.

CEI-LAB, Cornell University 2023
"""

from __future__ import print_function
import logging
import time
from multiprocessing import Lock

import RPi.GPIO as GPIO


import robot.configurations as config
import threading
from robot.controllers.bladder.bladder_motor import bladder_motor as motor_controller


class BladderController(object):
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(BladderController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        __init__ Create a Bladder Command object.  Takes in commands and performs the appropriate actions.
        """
        GPIO.setmode(GPIO.BCM)
        self.event = threading.Event()
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
        print("m3:", self.m3)
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

    async def move_all_dist(self, dist1, dist2, dist3, direction='out', speed=config.BLADDER_SPEED):
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
        self.m1Event.clear()
        self.m2Event.clear()
        self.m3Event.clear()
        self.m1.move_distance(direction, speed, dist1)
        self.m2.move_distance(direction, speed, dist2)
        self.m3.move_distance(direction, speed, dist3)

        await self.m1Event and self.m2Event and self.m3Event

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

    # def calibrate(self):
    #     self.m
