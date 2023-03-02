import subprocess
import sys
from pathlib import Path

from Configurations import *

"""
Implementation of SpeedController that will get speed from and set speed for 
the speed controller.

CEI-LAB, Cornell University 2019
"""


class SpeedController:

    def __init__(self, name, speed=0):
        self.name = name
        self.speed = speed
        self.cmd = CONFIGURATIONS.get("SPEED_CONTROLLER_COMMAND").format(home)
        self.d = '-d'

        self.resume()

    def __del__(self):
        self.stop()

    def set_speed(self, speed):
        if speed <= -3200 or speed >= 3200:
            pass
            # raise Exception('Speed should be between 0 and 3200. The values was {}'.format(speed))
        else:
            self.speed = speed
            logging.info([self.cmd, self.d, self.name, '--speed', str(self.speed)])
            subprocess.call(['sudo', self.cmd, self.d,
                             self.name, '--speed', str(self.speed)])

    def get_speed(self):
        return self.speed

    def brake(self, brake_speed):
        if brake_speed < 1 or brake_speed > 32:
            raise Exception(
                'Brake speed should be between 1 and 32. The values was {}'.format(brake_speed))
        else:
            self.speed = brake_speed
            subprocess.call(['sudo', self.cmd, self.d,
                             self.name, '--break', str(self.speed)])

    def stop(self):
        subprocess.call(['sudo', self.cmd, self.d, self.name, '--stop'])

    def resume(self):
        subprocess.call(['sudo', self.cmd, self.d, self.name, '--resume'])
