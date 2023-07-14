"""
A class to interact with the bladder motor controllers.
"""

from __future__ import print_function
import logging
import sys
import time
from multiprocessing import Lock
from pathlib import Path

import gpiozero as gpio

try:
    import RPi.GPIO as GPIO
except:
    logging.warning("Could not import RPi.GPIO, importing MOCK module instead")
    from robot.mock import MOCK_rpigpio as GPIO


import qwiic_scmd

import robot.configurations as config
import threading
from robot.commands.CommandInterface import CommandInterface

import math
import serial


class bladder_motor(object):
    def __init__(self, address, mot, event, enc1=None, enc2=None):
        """
        __init__ Motor controller for motors in the inflatable bladder.

        :param address: Address of motorcontroller
        :type address: int
        :param mot: ?possibly direction of motor?
        :type mot: bool
        :param event: Event for when motor is done with a movement
        :type event: Threading.event
        :param enc1: Encoder pin one, defaults to None
        :type enc1: int, optional
        :param enc2: Encoder pin two, defaults to None
        :type enc2: int, optional
        """
        self.motor = qwiic_scmd.QwiicScmd(address)
        if enc1 and enc2:
            # Set up GPIOs for encoders
            GPIO.setup(enc1, GPIO.IN)
            GPIO.setup(enc2, GPIO.IN)
            self.A = enc1
            self.B = enc2
            # Variables to store distance moved
            self.pos = 0
            self.state = 0
            if GPIO.input(enc1):
                self.state |= 1
            if GPIO.input(enc2):
                self.state |= 2

            # Variables used for moving the motors a specified distance
            self.init_pos = 0
            self.distance_to_move = 0
            self.move_dist = False

            # Calback function for encoder pins
            GPIO.add_event_detect(enc1, GPIO.BOTH, callback=self.__update)
            GPIO.add_event_detect(enc2, GPIO.BOTH, callback=self.__update)

            self.dir = 0
            self.mot = mot
            self.addr = address

            self.motor.begin()
            self.motor.set_drive(self.mot, self.dir, 0)
            self.motor.enable()
            time.sleep(0.250)

            self.mEvent = event

    def __update(self, channel):
        state = self.state & 3
        if GPIO.input(self.A):
            state |= 4
        if GPIO.input(self.B):
            state |= 8

        self.state = state >> 2

        if state == 1 or state == 7 or state == 8 or state == 14:
            self.pos += 1
        elif state == 2 or state == 4 or state == 11 or state == 13:
            self.pos -= 1
        elif state == 3 or state == 12:
            self.pos += 2
        elif state == 6 or state == 9:
            self.pos -= 2
        # Check if the motors need to stop
        if self.move_dist:
            # print(self.addr, self.mot, self.pos)
            if abs(self.pos - self.init_pos) >= self.distance_to_move:
                self.stop()

    def set_direction(self, direction):
        if direction == "out" or direction == 1:
            self.dir = 1
        elif direction == "in" or direction == 0:
            self.dir = 0

    def move_distance(self, direction, speed, distance):
        """
        move_distance Move a specified distance speed and direction.

        :param direction: Direction to move
        :type direction: _type_
        :param speed: Speed to move
        :type speed: int
        :param distance: Distance to move
        :type distance: int
        """

        if self.A and self.B:
            self.init_pos = self.pos
            self.distance_to_move = distance
            self.move_dist = True
            self.move(direction, speed)

    def stop(self):
        """
        stop Stop the motor clear any remaining move distance, and reset the init pos.
        """
        self.motor.set_drive(self.mot, self.dir, 0)
        self.init_pos = 0
        self.distance_to_move = 0
        self.move_dist = False

        self.mEvent.set()

    def move(self, direction, speed):
        self.set_direction(direction)
        self.motor.set_drive(self.mot, self.dir, speed)

    def enc_read(self):
        return self.pos
