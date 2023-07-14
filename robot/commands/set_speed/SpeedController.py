import subprocess
import sys
import logging
from pathlib import Path

import robot.configurations as config
"""
Implementation of SpeedController that will get speed from and set speed for 
the speed controller.

CEI-LAB, Cornell University 2019
"""


class SpeedController:

    def __init__(self, name, speed=0):
        self.name = name
        self.speed = speed
        self.cmd = config.SPEED_CONTROLLER_COMMAND
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
            # logging.info([self.cmd, self.d, self.name,
            #              '--speed', str(self.speed)])
            logging.info("calling set external")
            subprocess.call([self.cmd   + " " + self.d  + " " +  self.name  + " " +  '--speed' + " " + str(self.speed)],shell=True)

    def get_speed(self):
        return self.speed

    def brake(self, brake_speed):
        if brake_speed < 1 or brake_speed > 32:
            raise Exception(
                'Brake speed should be between 1 and 32. The values was {}'.format(brake_speed))
        else:
            self.speed = brake_speed
            subprocess.call([self.cmd   + " " + self.d  + " " +  self.name  + " " +  '--break' + " " + str(self.speed)])

    def stop(self):
        subprocess.call([self.cmd   + " " + self.d  + " " +  self.name  + " " +  '--stop'],shell=True)

    def resume(self):
        print(self.cmd)
        subprocess.call([self.cmd + " " + self.d + " " +  self.name + " " +  '--resume'],shell=True)
