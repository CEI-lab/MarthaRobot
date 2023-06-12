"""
Implementation of the main entry class for the HSI code. The responsibility of this class is to create various
functional threads and do necessary initializations.

CEI-LAB, Cornell University 2019
"""
import sys
import os

home = os.path.expanduser("~pi")

import numpy
import cv2
import os
import logging
import subprocess
import threading

# Utility Classes
import robot.configurations as config


# Command classes
from robot.commands.image.ImageCommand import ImageCommand
from robot.commands.tts.TextToSpeechCommand import TextToSpeechCommand
from robot.commands.tof.TimeofFlightCommand import TimeofFlightCommand
from robot.commands.sleep.SleepTwentySecsCommand import SleepTwentySecsCommand
from robot.commands.realsense.RealSenseCommand import RealSenseCommand
from robot.commands.hello.PrintHelloCommand import PrintHelloCommand
from robot.commands.external_camera.ExternalCameraCommand import ExternalCameraCommand
from robot.commands.image_names.GetImagesNamesCommand import GetImagesNamesCommand
from robot.commands.internal_camera.InternalCameraCommand import InternalCameraCommand
from robot.commands.set_speed.SetSpeedCommand import SetSpeedCommand
from robot.commands.imu.ReadIMUCommand import ReadIMUCommand
from robot.commands.set_speed.SetSpeedCommand import SetSpeedCommand
from robot.commands.bladder.BladderCommand import BladderCommand

# Command utilities
from robot.commands.CommandInterface import CommandInterface
from robot.commands.CommandRegistry import CommandRegistry
from robot.commands.CommandExecuter import CommandExecuter

# Resource classes
from robot.resources.queues.CommandQueue import CommandQueue
from robot.resources.queues.StatusQueue import StatusQueue

# Connections
from robot.tcp_manager.TCPManager import TCPManager
from robot.thread_manager.ThreadManager import ThreadManager


class HSIMaster(object):
    def __init__(self):
        if config.ENABLE_FILE_LOGGING:
            logging.basicConfig(
                filename=config.LOG_FILENAME.format(home), level=config.LOGGING_LEVEL
            )
        else:
            logging.basicConfig(
                level=config.LOGGING_LEVEL,
                format="[Time: %(relativeCreated)6d] " "[Thread: <%(threadName)s>] "
                # Uncomment the following line to include the function name in the log
                # '%(funcName)s in '
                "[File: {%(filename)s:%(lineno)d}] " "%(levelname)s - %(message)s",
            )

        # t1 = threading.Thread(target=self.displayHelper)
        # t1.start()

        self._command_event = threading.Event()
        self._status_event = threading.Event()

        self._my_singleton_received_command_queue = CommandQueue()
        self._my_singleton_status_queue = StatusQueue()
        self._my_singleton_command_registry = CommandRegistry()
        self._my_singleton_command_executor = CommandExecuter(
            self._my_singleton_received_command_queue,
            self._my_singleton_status_queue,
            self._my_singleton_command_registry,
            self._command_event,
            self._status_event,
        )
        self._my_singleton_tcp_manager = TCPManager(
            self._my_singleton_received_command_queue,
            self._my_singleton_status_queue,
            self._command_event,
            self._status_event,
        )
        # To create threads
        self._my_singleton_thread_manager = ThreadManager()
        # self._my_singleton_thread_manager.monitor_threads = True

    def displayHelper(self):
        # To add a blank image on startup
        subprocess.run(["xdotool", "mousemove", "9999", "9999"])
        cv2.namedWindow("window", cv2.WINDOW_FREERATIO)
        cv2.setWindowProperty("window", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        config.DISPLAY_IMAGE = numpy.ones((2, 2))
        while True:
            try:
                cv2.imshow("window", config.DISPLAY_IMAGE)
                cv2.waitKey(100)
            except:
                logging.error("IMAGE NOT DISPLAYABLE")

    def initializeCommandRegistry(self):
        self._my_singleton_command_registry.setObject(
            "PrintHelloCommand", PrintHelloCommand()
        )
        self._my_singleton_command_registry.setObject(
            "SleepTwentySecsCommand", SleepTwentySecsCommand()
        )
        self._my_singleton_command_registry.setObject(
            "TextToSpeechCommand", TextToSpeechCommand()
        )
        self._my_singleton_command_registry.setObject(
            "ExternalCameraCommand", ExternalCameraCommand()
        )
        self._my_singleton_command_registry.setObject(
            "InternalCameraCommand", InternalCameraCommand()
        )
        self._my_singleton_command_registry.setObject(
            "RealSenseCommand", RealSenseCommand()
        )
        self._my_singleton_command_registry.setObject("ImageCommand", ImageCommand())
        self._my_singleton_command_registry.setObject(
            "SetSpeedCommand", SetSpeedCommand()
        )
        self._my_singleton_command_registry.setObject(
            "TimeofFlightCommand", TimeofFlightCommand()
        )
        # self._my_singleton_command_registry.setObject("ReadIMUCommand", ReadIMUCommand())
        # self._my_singleton_command_registry.setObject("BladderCommand", BladderCommand())

    def startSystem(self):
        self._my_singleton_thread_manager.new_onetime(
            self._my_singleton_tcp_manager.listenTCP, "ListenTCP", True
        )
        self._my_singleton_thread_manager.new_periodic(
            self._my_singleton_tcp_manager.checkForNewIP,
            "CheckNewIP",
            config.CHECK_NEW_IP_FROM_PI_FREQUENCY,
            True,
        )
        self._my_singleton_thread_manager.new_onetime(
            self._my_singleton_tcp_manager.checkForStatus, "CheckStatusQueue", True
        )
        self._my_singleton_thread_manager.new_onetime(
            self._my_singleton_command_executor.checkForCommand,
            "CheckCommandQueue",
            True,
        )
        self._my_singleton_thread_manager.start_all()
        self._my_singleton_thread_manager.start()
        self._my_singleton_thread_manager.run_while_active()


if __name__ == "__main__":
    obj = HSIMaster()
    obj.initializeCommandRegistry()
    obj.startSystem()
