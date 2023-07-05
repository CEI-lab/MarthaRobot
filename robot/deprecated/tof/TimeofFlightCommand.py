import logging
import sys
import time
import random
import re
import os
import threading
from multiprocessing import Lock
from pathlib import Path
from robot.commands.CommandInterface import CommandInterface
import robot.configurations as config

# import VL53L0X
import adafruit_vl53l0x as VL53L0X

try:
    import RPi.GPIO as GPIO
except:
    logging.warning("Could not import RPi.GPIO, importing MOCK module instead")
    from robot.mock import MOCK_rpigpio as GPIO

from robot.commands.tof import TimeofFlightServer
import asyncore

"""
Implementation of TimeofFlightCommand that will produce sound from text in json object.

CEI-LAB, Cornell University 2019
"""


class TimeofFlightCommand(CommandInterface):
    streaming = False

    def execute_helper(self, responseStatusCallback, jsonObject):
        """
        Helper for :func:`execute()<robot.commands.tof.TimeofFlightCommand.TimeofFlightCommand.execute>`.


        :param responseStatusCallback: A callback function has to be passed, that will
                send status of command execution back to the controller. This callback will be passed by the
                caller of execute().
        :type responseStatusCallback: func
        :param jsonObject: A JSON object initially containing the command json, modified to include response information.
        :type jsonObject: dictionary

        :mod:`TimeofFlightCommand<robot.commands.tof
        """
        try:
            if jsonObject["type"] == "single":
                shutdown_pins = config.TOF_PINS
                GPIO.setmode(GPIO.BCM)

                for pin in shutdown_pins:
                    GPIO.setup(pin, GPIO.OUT)
                    GPIO.output(pin, GPIO.LOW)
                time.sleep(0.5)

                # TODO change to use config.TOF_ADDR[0-2]

                tof_objects = {}
                tof_objects[shutdown_pins[0]] = VL53L0X.VL53L0X(address=0x2A)
                tof_objects[shutdown_pins[1]] = VL53L0X.VL53L0X(address=0x2C)
                tof_objects[shutdown_pins[2]] = VL53L0X.VL53L0X(address=0x2E)

                for pin in shutdown_pins:
                    GPIO.output(pin, GPIO.HIGH)
                    time.sleep(0.50)
                    tof_objects[pin].start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)

                _ToF = [0, 0, 0]

                for i in range(3):
                    distance = tof_objects[shutdown_pins[i]].get_distance()
                    while distance == -1:
                        GPIO.output(shutdown_pins[i], GPIO.LOW)
                        time.sleep(0.1)
                        GPIO.output(shutdown_pins[i], GPIO.HIGH)
                        time.sleep(0.1)
                        tof_objects[shutdown_pins[i]].start_ranging(
                            VL53L0X.VL53L0X_BETTER_ACCURACY_MODE
                        )
                    _ToF[i] = distance

                GPIO.cleanup()

                jsonObject["data"] = _ToF
            if jsonObject["type"] == "stream":
                if "count_period" in jsonObject:
                    config.TIMEOFFLIGHT_COUNT_PERIOD = jsonObject["count_period"]
                if self.streaming == False:
                    self.server = TimeofFlightServer.TOFMulticastServer()
                    self.streaming = True
                    if responseStatusCallback is not None:
                        responseStatusCallback(jsonObject)
                    asyncore.loop()
            if jsonObject["type"] == "stop" and self.streaming:
                self.streaming = False
                self.server.closeServer()
        except:
            logging.error("ToFCommand : error in jsonObject")
        finally:
            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)

    def execute(self, responseStatusCallback, jsonObject):
        """
        This method will create a thread to execute the input command.

        :param responseStatusCallback: A callback function has to be passed, that will
                        send status of command execution back to the controller. This callback will be passed by the
                        caller of execute().
        :type responseStatusCallback: func(jsonObject) ->
        :param jsonObject: A JSON object initially containing the command json, modified to include response information.
        :type jsonObject: dictionary
        """

        t1 = threading.Thread(
            target=self.execute_helper,
            args=(
                responseStatusCallback,
                jsonObject,
            ),
        )
        t1.start()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.ERROR,
        format="[Time: %(relativeCreated)6d] "
        "[Thread: <%(threadName)s>] "  # Uncomment the following line to include the function name in the log
        # '%(funcName)s in '
        "[File: {%(filename)s:%(lineno)d}] " "%(levelname)s - %(message)s",
    )

    obj1 = TimeofFlightCommand()
    obj1.execute(None, {"startSendingToF": True, "countPeriod": 3})
    time.sleep(5)
    obj1.execute(None, {"startSendingToF": True, "countPeriodXX": 1})
    time.sleep(5)

    obj2 = TimeofFlightCommand()
    print("<<<<<<<<<<<<< stop reading with new singelton class >>>>>>>>>>>>>>>")
    obj2.execute(None, {"startSendingToF": False})
    obj2.execute(None, {"startSendingToF": False})
