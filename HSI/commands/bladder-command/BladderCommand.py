from __future__ import print_function
import logging
import sys
import time
import serial
from multiprocessing import Lock
from pathlib import Path

import gpiozero as gpio
import Encoder
import RPi.GPIO as GPIO
import math
import qwiic_scmd

from Configurations import *
import threading
from CommandInterface import CommandInterface

"""
Implementation of BladderCommand that will produce sound from text in json object.

CEI-LAB, Cornell University 2019
"""

class Motor(object):
    def __init__(self, address, mot, event, enc1 = None, enc2 = None):
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
            GPIO.add_event_detect(enc1, GPIO.BOTH, callback = self.__update)
            GPIO.add_event_detect(enc2, GPIO.BOTH, callback = self.__update)
            
            self.dir = 0
            self.mot = mot
            self.addr = address
            
            self.motor.begin()
            self.motor.set_drive(self.mot, self.dir, 0)
            self.motor.enable()
            time.sleep(.250)
            
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
            #print(self.addr, self.mot, self.pos)
            if abs(self.pos - self.init_pos) >= self.distance_to_move:
                self.stop()
        
        
    def set_direction(self, direction):
        if direction == 'out' or direction == 1:
            self.dir = 1
        elif direction == 'in' or direction == 0:
            self.dir = 0
 
    def move_distance(self, direction, speed, distance):
        if self.A and self.B:
            self.init_pos = self.pos
            self.distance_to_move = distance
            self.move_dist = True
            self.move(direction, speed)
        
    def stop(self):
        #print("Stopping")
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

class BladderCommand(CommandInterface):
    _t1 = None
    #_lock = Lock()
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.MOTOR_A = 0
        self.MOTOR_B = 1
        self.FWD = 0
        self.BWD = 1
        
        self.enc11 = 17
        self.enc12 = 18
        self.enc21 = 11
        self.enc22 = 5
        self.enc31 = 19
        self.enc32 = 6
        
        self.m1Event = threading.Event()
        self.m2Event = threading.Event()
        self.m3Event = threading.Event()
        
        self.m1 = Motor(0x5E, 1, self.m1Event, self.enc11, self.enc12)
        self.m2 = Motor(0x5E, 0, self.m2Event, self.enc21, self.enc22)
        self.m3 = Motor(0x5D, 0, self.m3Event, self.enc31, self.enc32)
        
        GPIO.setup(21, GPIO.OUT)
        self.fan = GPIO.PWM(21, 1000)
        self.fan.start(0)
    
    def __del__(self):
        self.m1.motor.disable()
        self.m2.motor.disable()
        self.m3.motor.disable()
        self.fan.stop()
        
    def stop(self):
        self.m1.stop()
        self.m2.stop()
        self.m3.stop()
     
    def move_all(self, direction, speed):
        self.m1.move(direction, speed)
        self.m2.move(direction, speed)
        self.m3.move(direction, speed)
     
    def move_all_dist(self, dist1, dist2, dist3, direction, speed):
        self.m1.move_distance(direction, speed, dist1)
        self.m2.move_distance(direction, speed, dist2)
        self.m3.move_distance(direction, speed, dist3)
     
    def inflate(self):
        self.fan.ChangeDutyCycle(100)
        time.sleep(10)
        self.m1Event.clear()
        self.m2Event.clear()
        self.m3Event.clear()
        self.move_all_dist(168, 168, 168, 'out', 250)
        self.m1Event.wait()
        self.m2Event.wait()
        self.m3Event.wait()
     
    def deflate(self):
        self.fan.ChangeDutyCycle(100)
        self.m1Event.clear()
        self.m2Event.clear()
        self.m3Event.clear()
        self.move_all_dist(168, 168, 168, 'in', 250)
        self.m1Event.wait()
        self.m2Event.wait()
        self.m3Event.wait()
        self.fan.ChangeDutyCycle(0)
    
    def _inflate_deflate(self, responseStatusCallback, jsonObject):
        """
        This method will be called to inflate and deflate the air channels.

        Inputs:
            responseStatusCallback : A callback function has to be passed, that will
                send status of command execution. This callback will be passed by the
                caller of execute().
            jsonObject : A JSON object containing text.

        Outputs:
            None
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
                    logging.info('BladderCommand : There is a typo in the action field.')
                    jsonObject["response"] = "INCORRECT_INFLATE_DEFLATE_FIELD"
                       
            except:
                logging.info('BladderCommand : can\'t open serial port.')
                jsonObject["response"] = "SERIAL_CONNECTION_CLOSED"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            logging.error('BladderCommand : Error probably in responseStatus call or resource is busy')


    def execute(self, responseStatusCallback, jsonObject):
        try:
            jsonObject["response"] = "ACTION_OR_SELECT_FIELD_NOT_IN_JSON"
            if "action" in jsonObject:
                self._t1 = threading.Thread(target=self._inflate_deflate, args=(responseStatusCallback, jsonObject,))
                self._t1.start()
                logging.info('BladderCommand : Process bladder command')
                jsonObject["response"] = "PROCESS_BLADDER_COMMAND"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            logging.error('BladderCommand : Error no action or select field in json object')


if __name__ == "__main__":
    obj = BladderCommand()
    obj.execute(None, {"select" : [1,0,0],'action': "inflate"})
