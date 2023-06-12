import gpiozero as gpio
import time
import Encoder
import logging

try:
    import RPi.GPIO as GPIO
except:
    logging.warning("Could not import RPi.GPIO, importing MOCK module instead")
    from robot.mock import MOCK_rpigpio as GPIO


class Motor(object):
    def __init__(
        self, m_pin, dir_1, dir_2, enc1=None, enc2=None, polarity=0, freq=1000
    ):
        self.motor = gpio.PWMOutputDevice(m_pin, frequency=freq)

        if enc1 and enc2:
            # Set up GPIOs for encoders
            GPIO.setmode(GPIO.BCM)
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

        # Check the polarity of the motor
        if not polarity:
            self.dir1 = gpio.DigitalOutputDevice(dir_1)
            self.dir2 = gpio.DigitalOutputDevice(dir_2)
        else:
            self.dir1 = gpio.DigitalOutputDevice(dir_2)
            self.dir2 = gpio.DigitalOutputDevice(dir_1)

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
            if abs(self.pos - self.init_pos) > self.distance_to_move:
                self.stop()

    def set_direction(self, direction):
        if direction == "out" or direction == 1:
            self.dir1.on()
            self.dir2.off()
        elif direction == "in" or direction == 0:
            self.dir1.off()
            self.dir2.on()
        elif direction == "stop" or direction < 1:
            self.dir1.off()
            self.dir2.off()

    def move_distance(self, direction, speed, distance):
        if self.A and self.B:
            self.init_pos = self.pos
            self.distance_to_move = distance
            self.move_dist = True
            self.move(direction, speed)

    def stop(self):
        self.motor.off()
        self.init_pos = 0
        self.distance_to_move = 0
        self.move_dist = False

    def move(self, direction, speed):
        self.set_direction(direction)
        self.motor.value = speed * 0.5

    def enc_read(self):
        return self.pos

    def get_direction(self):
        if self.dir1.value and not self.dir2.value:
            return "out"
        elif not self.dir1.value and self.dir2.value:
            return "in"
        else:
            return "stop"

    def get_speed(self):
        return self.motor.value


m1_dir1 = 10
m1_dir2 = 18
m1_pwm = 17
m2_dir1 = 24
m2_dir2 = 15
m2_pwm = 16
m3_dir1 = 0
m3_dir2 = 22
m3_pwm = 23

enc11 = 9
enc12 = 11
enc21 = 25
enc22 = 5
enc31 = 20
enc32 = 12


m1 = Motor(m1_pwm, m1_dir1, m1_dir2, enc11, enc12, 0)
m2 = Motor(m2_pwm, m2_dir1, m2_dir2, enc21, enc22, 0)
m3 = Motor(m3_pwm, m3_dir1, m3_dir2, enc31, enc32, 1)
fan = gpio.PWMOutputDevice(21, 1000)


def stop():
    m1.stop()
    m2.stop()
    m3.stop()


def move_all(direction, speed):
    m1.move(direction, speed)
    m2.move(direction, speed)
    m3.move(direction, speed)


def read():
    print("M1 Reading: ", m1.enc_read())
    print("M2 Reading: ", m2.enc_read())
    print("M3 Reading: ", m3.enc_read())


def move_all_dist(dist1, dist2, dist3, direction, speed):
    m1.move_distance(direction, speed, dist1)
    m2.move_distance(direction, speed, dist2)
    m3.move_distance(direction, speed, dist3)


def inflate():
    fan.value = 1
    time.sleep(5)
    move_all_dist(181110, 180783, 181154, "out", 1)


def deflate():
    fan.value = 0.3
    move_all_dist(181110, 180783, 181154, "in", 1)
    time.sleep(10)
    fan.value = 0.2
    time.sleep(10)
    fan.value = 0.1
    time.sleep(20)
    fan.value = 0
