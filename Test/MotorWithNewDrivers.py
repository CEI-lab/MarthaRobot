from __future__ import print_function
import gpiozero as gpio
import time
import Encoder
import logging

try:
    import RPi.GPIO as GPIO
except:
    logging.warning("Could not import RPi.GPIO, importing MOCK module instead")
    from robot.mock import MOCK_rpigpio as GPIO

import sys
import math
import qwiic_scmd
import threading

MOTOR_A = 0
MOTOR_B = 1
FWD = 0
BWD = 1

enc11 = 17
enc12 = 18
enc21 = 11
enc22 = 5
enc31 = 19
enc32 = 6

GPIO.setmode(GPIO.BCM)

m1Event = threading.Event()
m2Event = threading.Event()
m3Event = threading.Event()


class Motor(object):
    def __init__(self, address, mot, event, enc1=None, enc2=None):
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
            print(self.addr, self.mot, self.pos)
            if abs(self.pos - self.init_pos) >= self.distance_to_move:
                self.stop()
                # print(self.addr, self.mot)

    #
    #     def __update(self, channel):
    #         outcome = [0, 1, -1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0]
    #         in1 = GPIO.input(self.A)
    #         in2 = GPIO.input(self.B)
    #         curr = (in1 << 1) | in2
    #         currPos = (self.last << 2) | curr
    #         self.pos += outcome[currPos]
    #         self.last = curr
    #         if self.move_dist:
    #             print(self.pos - self.init_pos, self.distance_to_move, self.addr, self.mot)
    #             if abs(self.pos - self.init_pos) > self.distance_to_move:
    #                 self.stop()
    #                 #print(self.addr, self.mot)

    def set_direction(self, direction):
        if direction == "out" or direction == 1:
            self.dir = 1
        elif direction == "in" or direction == 0:
            self.dir = 0

    def move_distance(self, direction, speed, distance):
        if self.A and self.B:
            self.init_pos = self.pos
            self.distance_to_move = distance
            self.move_dist = True
            self.move(direction, speed)

    def stop(self):
        # print("Stopping")
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


m1 = Motor(0x5E, 1, m1Event, enc11, enc12)
m2 = Motor(0x5E, 0, m2Event, enc21, enc22)
m3 = Motor(0x5D, 0, m3Event, enc31, enc32)

GPIO.setup(21, GPIO.OUT)
fan = GPIO.PWM(21, 1000)
fan.start(0)


def stop():
    m1.stop()
    m2.stop()
    m3.stop()


def move_all(direction, speed):
    m1.move(direction, speed)
    m2.move(direction, speed)
    m3.move(direction, speed)


def move_all_dist(dist1, dist2, dist3, direction, speed):
    m1.move_distance(direction, speed, dist1)
    m2.move_distance(direction, speed, dist2)
    m3.move_distance(direction, speed, dist3)


def inflate():
    print("Inflating...")
    fan.ChangeDutyCycle(100)
    # time.sleep(10)
    m1Event.clear()
    m2Event.clear()
    m3Event.clear()
    move_all_dist(12, 12, 12, "out", 250)
    m1Event.wait()
    m2Event.wait()
    m3Event.wait()


def deflate():
    print("Deflating...")
    fan.ChangeDutyCycle(70)
    m1Event.clear()
    m2Event.clear()
    m3Event.clear()
    move_all_dist(12, 12, 12, "in", 250)
    m1Event.wait()
    m2Event.wait()
    m3Event.wait()
    fan.ChangeDutyCycle(0)


if __name__ == "__main__":
    try:
        for j in range(30000):
            inflate()
            time.sleep(5)
            deflate()
            print("Done: " + str(j))
            time.sleep(5)
        # time.sleep(30)
        # deflate()
        # time.sleep(30)
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("Ending example.")
    finally:
        print("Ending example.")
        m1.motor.disable()
        m2.motor.disable()
        m3.motor.disable()
        fan.stop()
        GPIO.cleanup()
        sys.exit(0)
