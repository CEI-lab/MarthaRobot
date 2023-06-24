from pathlib import Path
from multiprocessing import Lock
import sys
import os
import threading
import time
import logging
from math import cos, sin, radians
from robot.commands.imu.get_imu import *
from robot.commands.imu.get_mag import *

import robot.configurations as config
from robot.commands.CommandInterface import CommandInterface


"""
Implementation of ReadIMUCommand that will read IMU accelerometer data once, 
and send it over remote controller using responseStatusCallback.

CEI-LAB, Cornell University 2019
"""


class ReadIMUCommand(CommandInterface):

    _lock = Lock()

    # factors for conversion
    _acc_fact = 32768.0 / 2.0  # range 2G
    _gyr_fact = 32768.0 / 2000.0  # range 2000 deg/s
    _gravity = 9.806

    def _readIMUHelper(self, responseStatusCallback, jsonObject):
        """
        This method will read IMU (BMI160) once, and output whether the rover
        is flipped or not. 

        Inputs:
            responseStatusCallback : A callback function has to be passed, that will
                send status of command execution. This callback will be passed by the
                caller of execute().
            jsonObject : A JSON object containing remote IP and remote folder.

        Outputs:
            None
        """

        try:
            self._lock.acquire()
            jsonObject["response"] = "UNKNOWN_ERROR"

            try:
                # configure BMI160
                bmi160 = configure_bmi160()

                try:
                    sensor_return = read_raw_sensors(bmi160)

                    if (sensor_return != -1):
                        [gx, gy, gz, ax, ay, az] = sensor_return

                        # angular velocity
                        jsonObject["angular velocity"] = [round(radians(gx / self._gyr_fact), 3),
                                                          round(
                                                              radians(gy / self._gyr_fact), 3),
                                                          round(radians(gz / self._gyr_fact), 3)]
                        # linear acceleration
                        jsonObject["accelerometer"] = [round((ax / self._acc_fact) * self._gravity, 3),
                                                       round(
                                                           (ay / self._acc_fact) * self._gravity, 3),
                                                       round((az / self._acc_fact) * self._gravity, 3)]

                        if (jsonObject["accelerometer"][2] > 0):
                            jsonObject["roverFlipped"] = False
                        else:
                            jsonObject["roverFlipped"] = True

                        jsonObject["response"] = "SUCCESS"

                    else:
                        logging.error(
                            'ReadIMUCommand : IMU reading return error')
                        jsonObject["response"] = "DATA_ERROR"
                except:
                    logging.error('ReadIMUCommand : IMU reading error')
                    jsonObject["response"] = "READING_ERROR"
            except:
                logging.error('ReadIMUCommand : IMU (BMI160) configure error')
                jsonObject["response"] = "IMU_CONFIG_ERROR"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)

        except:
            logging.error('ReadIMUCommand : unknown error')
        finally:
            self._lock.release()

    def execute(self, responseStatusCallback, jsonObject):
        try:
            t1 = threading.Thread(target=self._readIMUHelper, args=(
                responseStatusCallback, jsonObject,))
            t1.start()
        except:
            logging.error('ReadIMUCommand : error in threading')


if __name__ == "__main__":
    obj = ReadIMUCommand()
    obj.execute(None, {'cmd': 'ReadIMUCommand', 'priority': 1})
    time.sleep(1)
    obj.execute(None, {'cmd': 'ReadIMUCommand', 'priority': 1})
