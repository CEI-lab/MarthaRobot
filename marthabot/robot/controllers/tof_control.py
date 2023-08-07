


import threading
import logging
import sys
import time
import random
import re
import os
import threading
from multiprocessing import Lock
from pathlib import Path

import marthabot.configurations.robot_config as config
# import VL53L0X
import adafruit_vl53l0x as VL53L0X

log = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except:
    logging.warning("Could not import RPi.GPIO, importing MOCK module instead")
    from marthabot.robot.mock import MOCK_rpigpio as GPIO

from marthabot.robot.commands.tof import tof_server

import board

def list_i2c():
    i2c = board.I2C()
    scan = i2c.scan()
    for addr in scan:
        print(hex(addr))
    i2c.deinit()


class SingletonTOFControl:
    __instance = None
    __initialized = False
    __lock = threading.Lock()


    def __new__(cls):
        if cls.__instance is None:
            with cls.__lock:
                if cls.__instance is None:
                    cls.__instance = super().__new__(cls)

        return cls.__instance


    def __init__(self, drive_controller = None):
        if self.__initialized:
            log.warning("Attempted to re-initialize the SingletonTOFControl")
            return
        else:
            self.__initialized = True
        
        log.info("Initializing SingletonTOFControl. ")

        self.drive_controller = drive_controller
        
        self.shutdown_pins = config.TOF_PINS

        GPIO.setmode(GPIO.BCM)

        # setup shutdown pins, and shutdown all vl53 sensors
        for pin in self.shutdown_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        time.sleep(0.5)
        
        i2c = board.I2C()
        self.tof_objects : list[VL53L0X.VL53L0X]= []
        # [VL53L0X.VL53L0X(i2c=i2c, address=config.TOF_DEFAULT_ADDR) for i in config.TOF_ADDR]

        # create TOF objects and change I2C addresses
        for pin, new_addr in zip(config.TOF_PINS, config.TOF_ADDR):
            GPIO.output(pin, GPIO.HIGH)
            sensor = VL53L0X.VL53L0X(i2c=i2c, address=config.TOF_DEFAULT_ADDR) 
            sensor.set_address(new_addr)
            time.sleep(0.5) #TODO decrease the sleeps in this init
            

            self.tof_objects.append(sensor)

        self._dists = [0, 0, 0]
    

    

    def get_dists(self):
        # bogus = [1.0,2.0,3.0]
        # random.shuffle(bogus)
        # return bogus
        # dists = []
        # for tof in self.tof_objects:
        #     dists.append(tof.range)
        # print(self.tof_objects[0].range)
        dists = [tof.range for tof in self.tof_objects]
        # time.sleep(0.1)
        return dists 
    
if __name__ == "__main__":
    tof = SingletonTOFControl()
    tof1 = SingletonTOFControl()
    tof2 = SingletonTOFControl()
    tof3 = SingletonTOFControl()
    tof4 = SingletonTOFControl()

    LINE_UP = '\033[1A'
    LINE_CLEAR = '\x1b[2K'

    # list_i2c()

    print("Displaying TOF distances:")
    try:
        while True:
            dists = tof.get_dists()
            for i in range(len(dists)):
                s = str(dists[i])
                dists[i] = s.ljust(6," ")
            # print(LINE_UP + LINE_CLEAR)
            print("\b"* len(str(dists)), end="",flush=False)            
            print(dists,end="",flush=True)
            # time.sleep(0.1)
    finally:
        GPIO.cleanup()