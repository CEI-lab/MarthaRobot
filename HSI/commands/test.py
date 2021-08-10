import sys
import signal
from gpiozero import DigitalInputDevice
import gpiozero as gpio
from time import sleep

from Configurations import *


def move_motor_n_turns(motor, n):
	

