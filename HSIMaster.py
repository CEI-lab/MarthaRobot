import os
import sys
import time
import logging
import json
from pathlib import Path
from Configurations import *
import numpy
import subprocess
import threading

sys.path.append(home + "/HSI/commands/")
sys.path.append(home + "/HSI/thread/")
sys.path.append(home + "/HSI/commands/")
sys.path.append(home + "/HSI/commands/text-to-speech-command")
sys.path.append(home + "/HSI/commands/external-camera-command")
sys.path.append(home + "/HSI/commands/internal-camera-command")
sys.path.append(home + "/HSI/commands/real-sense-command")
sys.path.append(home + "/HSI/commands/image-command")
sys.path.append(home + "/HSI/commands/get-images-names-command")
sys.path.append(home + "/HSI/commands/set-speed-command")
sys.path.append(home + "/HSI/commands/time-of-flight-command")
sys.path.append(home + "/HSI/commands/read-IMU-command")
sys.path.append(home + "/HSI/commands/bladder-command")
sys.path.append(home + "/HSI/command-executer")
sys.path.append(home + "/HSI/resources/RealSense/")
sys.path.append(home + "/HSI/resources/registries/")
sys.path.append(home + "/HSI/resources/queues/")
sys.path.append(home + "/HSI/resources/classes")
sys.path.append(home + "/HSI/tcp-manager")

sys.path.append(home + "/.local/lib/python3.7/site-packages/")

import cv2

# Utility Classes
from ThreadManager import ThreadManager
from TCPManager import TCPManager
from CommandRegistry import CommandRegistry
from CommandExecuter import CommandExecuter

# Resource classes
from StatusQueue import StatusQueue
from CommandQueue import CommandQueue

# Command classes
from TextToSpeechCommand import TextToSpeechCommand
from ExternalCameraCommand import ExternalCameraCommand
from InternalCameraCommand import InternalCameraCommand
from RealSenseCommand import RealSenseCommand
from ImageCommand import ImageCommand
from SetSpeedCommand import SetSpeedCommand
from TimeofFlightCommand import TimeofFlightCommand
from ReadIMUCommand import ReadIMUCommand
from BladderCommand import BladderCommand

"""
Implementation of the main entry class for the HSI code. The responsibility of this class is to create various
functional threads and do necessary initializations.

CEI-LAB, Cornell University 2019
"""


class HSIMaster(object):

    def __init__(self):
        if CONFIGURATIONS.get("ENABLE_FILE_LOGGING"):
            logging.basicConfig(filename=CONFIGURATIONS.get("LOG_FILENAME").format(home),
                                level=CONFIGURATIONS.get("LOGGING_LEVEL"))
        else:
            logging.basicConfig(level=CONFIGURATIONS.get("LOGGING_LEVEL"),
                                format='[Time: %(relativeCreated)6d] ' \
                                       '[Thread: <%(threadName)s>] '
                                # Uncomment the following line to include the function name in the log
                                # '%(funcName)s in '
                                       '[File: {%(filename)s:%(lineno)d}] '
                                       '%(levelname)s - %(message)s')

        t1 = threading.Thread(target=self.displayHelper)
        t1.start()

        self._my_singleton_received_command_queue = CommandQueue()
        self._my_singleton_status_queue = StatusQueue()
        self._my_singleton_command_registry = CommandRegistry()
        self._my_singleton_command_executor = CommandExecuter(self._my_singleton_received_command_queue,
                                                              self._my_singleton_status_queue,
                                                              self._my_singleton_command_registry)
        self._my_singleton_tcp_manager = TCPManager(self._my_singleton_received_command_queue,
                                                    self._my_singleton_status_queue)
        # To create threads
        self._my_singleton_thread_manager = ThreadManager()
        self._my_singleton_thread_manager.monitor_threads = True
    def displayHelper(self):
        # To add a blank image on startup
        subprocess.run(["xdotool","mousemove","9999","9999"])
        cv2.namedWindow("window", cv2.WINDOW_FREERATIO)
        cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        CONFIGURATIONS["DISPLAY_IMAGE"] = numpy.ones((2,2))
        while True:
            try:
                cv2.imshow('window', CONFIGURATIONS["DISPLAY_IMAGE"])
                cv2.waitKey(100)
            except:
                logging.error("IMAGE NOT DISPLAYABLE")
    def initializeCommandRegistry(self):
        self._my_singleton_command_registry.setObject("TextToSpeechCommand", TextToSpeechCommand())
        self._my_singleton_command_registry.setObject("ExternalCameraCommand", ExternalCameraCommand())
        self._my_singleton_command_registry.setObject("InternalCameraCommand", InternalCameraCommand())
        self._my_singleton_command_registry.setObject("RealSenseCommand", RealSenseCommand())
        self._my_singleton_command_registry.setObject("ImageCommand", ImageCommand())
        self._my_singleton_command_registry.setObject("SetSpeedCommand", SetSpeedCommand())
        self._my_singleton_command_registry.setObject("TimeofFlightCommand", TimeofFlightCommand())
        #self._my_singleton_command_registry.setObject("ReadIMUCommand", ReadIMUCommand())
        #self._my_singleton_command_registry.setObject("BladderCommand", BladderCommand())

    def startSystem(self):
        self._my_singleton_thread_manager.new_onetime(self._my_singleton_tcp_manager.listenTCP, 'ListenTCP', True)
        self._my_singleton_thread_manager.new_periodic(self._my_singleton_tcp_manager.checkForNewIP, 'CheckNewIP',
                                                       CONFIGURATIONS.get("CHECK_NEW_IP_FROM_PI_FREQUENCY"), True)
        self._my_singleton_thread_manager.new_onetime(self._my_singleton_tcp_manager.checkForStatus, 'CheckStatusQueue',
                                                      True)
        self._my_singleton_thread_manager.new_onetime(self._my_singleton_command_executor.checkForCommand,
                                                      'CheckCommandQueue', True)
        self._my_singleton_thread_manager.start_all()
        self._my_singleton_thread_manager.start()
        self._my_singleton_thread_manager.run_while_active()


if __name__ == '__main__':
    obj = HSIMaster()
    obj.initializeCommandRegistry()
    obj.startSystem()
