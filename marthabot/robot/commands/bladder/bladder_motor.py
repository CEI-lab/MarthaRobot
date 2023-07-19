"""
A class to interact with the bladder motor controllers.
"""

from __future__ import print_function
import asyncio
from enum import Enum
import logging
import sys
import time
from multiprocessing import Lock
from pathlib import Path
import logging
log = logging.getLogger(__name__)

import gpiozero as gpio

try:
    import RPi.GPIO as GPIO
except:
    logging.warning("Could not import RPi.GPIO, importing MOCK module instead")
    from marthabot.robot.mock import MOCK_rpigpio as GPIO

from marthabot.robot.resources.event_utils import ChildEvent, AndEvent


import qwiic_scmd

import marthabot.configurations.robot_config as config
import threading

import math
import serial

class Status(Enum):
    ERROR = -1
    INITIALIZED = 0
    MOVE_DIST = 1
    MOVE = 2
    STOPPED = 3
    END_STOPPED = 4
    WAITING = 5

# TODO select wait implementation that is most efficient

class bladder_motor(object):

    def __init__(self, address, mot, event, enc1=None, enc2=None):
        """
        __init__ Motor controller for motors in the inflatable bladder.

        :param address: Address of motorcontroller
        :type address: int
        :param mot: Motor selector
        :type mot: int
        :param event: Event for when motor is done with a movement
        :type event: Threading.event
        :param enc1: Encoder pin one, defaults to None
        :type enc1: int, optional
        :param enc2: Encoder pin two, defaults to None
        :type enc2: int, optional
        """
        self._address = address
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
            
            self.iEvent = ChildEvent()
            self.timeout = asyncio.timeout()
            self.last_pos = 0

            self.status = Status.INITIALIZED
            log.debug(f"Initialized motor {self._address} for the bladder")
        else:
            log.error(f"Failed to initialize a bladder motor")
            self.status = Status.ERROR

    def reset(self):
        self.stop()
        self.pos = 0
        self.init_pos = 0
        self.distance_to_move = 0
        self.state = Status.STOPPED

    def _reschedule(self):
        deadline = asyncio.get_running_loop().time() + config.MOTOR_TIMEOUT
        self.timeout.reschedule(deadline)

    async def wait(self):
        """
        wait wait for motor to finish moving, while checking 
        """
        try:
            async with self.timeout:
                self._reschedule()
                await(self.mEvent)
                self.state = "Finished"
        except TimeoutError:
            self.status = Status.END_STOPPED
            log.warning(f"Motor {self._address} was stopped due to lack of motion.")

    async def wait2(self):
        """
        wait2 Alternate wait implementation that may be more computationally efficient
        """
        self.iEvent.set()
        while not self.mEvent.is_set():
            try:
                async with asyncio.timeout(config.MOTOR_TIMEOUT):
                    await(self.mEvent)
            except TimeoutError:
                if self.iEvent.is_set():
                    self.iEvent.clear()
                else:
                    self.status = Status.END_STOPPED
                    log.warning(f"Motor {self._address} was stopped due to lack of motion.")
                    self.mEvent.set()

    async def wait3(self):
        """
        wait3 Alternate wait implementation that may be more computationally efficient
        """
        while not self.mEvent.is_set():
            try:
                async with asyncio.timeout(config.MOTOR_TIMEOUT):
                    await(self.mEvent)
            except TimeoutError:
                if self.pos == self.last_pos:
                    self.status = Status.END_STOPPED
                    log.warning(f"Motor {self._address} was stopped due to lack of motion.")
                    self.mEvent.set()
                else:
                    self.last_pos = self.pos


    def __update(self, channel):
        
        self.iEvent.set()
        self._reschedule()

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
        if self.status == Status.MOVE_DIST:
            # print(self.addr, self.mot, self.pos)
            if abs(self.pos - self.init_pos) >= self.distance_to_move:
                self.stop()



    def set_direction(self, direction):
        if direction == "out" or direction == 1:
            self.dir = 1
        elif direction == "in" or direction == 0:
            self.dir = 0

    async def move_distance(self, direction, speed, distance):
        """
        move_distance Move a specified distance speed and direction.

        :param direction: Direction to move
        :type direction: _type_
        :param speed: Speed to move
        :type speed: int
        :param distance: Distance to move
        :type distance: int
        """
        self.status = Status.MOVE_DIST
        if self.A and self.B:
            self.init_pos = self.pos
            self.distance_to_move = distance
            self.set_direction(direction)
            self.motor.set_drive(self.mot, self.dir, speed)
            self.move(direction, speed)
        self.wait()

    def stop(self):
        """
        Stop the motor clear any remaining move distance, and reset the init pos.
        """
        self.status = Status.STOPPED
        self.motor.set_drive(self.mot, self.dir, 0)
        self.init_pos = 0
        self.distance_to_move = 0
        self.mEvent.set()

    def move(self, direction, speed):
        self.status = Status.MOVE
        self.set_direction(direction)
        self.motor.set_drive(self.mot, self.dir, speed)

    def enc_read(self):
        return self.pos
