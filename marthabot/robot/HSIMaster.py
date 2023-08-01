"""
Implementation of the main entry class for the HSI code. The responsibility of this class is to create various
functional threads and do necessary initializations.

CEI-LAB, Cornell University 2019
"""
# from SleepTwentySecsCommand import SleepTwentySecsCommand
# from PrintHelloCommand import PrintHelloCommand
# from BladderCommand import BladderCommand
# from ReadIMUCommand import ReadIMUCommand
# from TimeofFlightCommand import TimeofFlightCommand
# from SetSpeedCommand import SetSpeedCommand
# from ImageCommand import ImageCommand
# from RealSenseCommand import RealSenseCommand
# from InternalCameraCommand import InternalCameraCommand
# from ExternalCameraCommand import ExternalCameraCommand
# from TextToSpeechCommand import TextToSpeechCommand
# from CommandQueue import CommandQueue
# from StatusQueue import StatusQueue
# from CommandExecuter import CommandExecuter
# from CommandRegistry import CommandRegistry
# from TCPManager import TCPManager
# from ThreadManager import ThreadManager
from cgi import test
import signal
import cv2
import os
import sys
import time
import logging
import json
from pathlib import Path
import numpy
import subprocess
import threading
import atexit

log = logging.getLogger(__name__)


home = os.path.expanduser("~pi")

# add some directories to path since the installations are a bit wonky
sys.path.append(home + "/HSI/resources/RealSense/")
sys.path.append(home + "/.local/lib/python3.7/site-packages/")


# Configurations for the robot
import marthabot.configurations.robot_config as config

from marthabot import robot
# from marthabot.robot import commands
import robot.commands

# help(robot)

# Command classes
from commands import (
    CommandInterface,
    CommandRegistry,
    CommandExecuter,
# )
# from commands import (
    BladderCommand,
    ExternalCameraCommand,
    ImageCommand,
    GetImagesNamesCommand,
    InternalCameraCommand,
    PrintHelloCommand,
    ReadIMUCommand,
    RealSenseCommand,
    SetSpeedCommand,
    SleepTwentySecsCommand,
    TextToSpeechCommand,
    TimeofFlightCommand,
)

# Resource classes
from robot.resources.queues.CommandQueue import CommandQueue
from robot.resources.queues.StatusQueue import StatusQueue

# Connections
from robot.tcp_manager.TCPManager import TCPManager
from robot.thread_manager.ThreadManager import ThreadManager

# from utils.custom_logger import CustomLogRecord, CustomLogger
# logging.setLoggerClass(CustomLogger)
# logging.setLogRecordFactory(CustomLogRecord)
# log = logging.getLogger("marthabot")

# loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
# for logger in loggers:
#     print(logger, logger.handlers)


class HSIMaster(object):
    def __init__(self):
        # logging now setup by utils/custom_logger

        # if config.ENABLE_FILE_LOGGING:
        #     logging.basicConfig(
        #         filename=config.LOG_FILENAME.format(home), level=config.LOGGING_LEVEL
        #     )
        # else:
        #     logging.basicConfig(
        #         level=config.LOGGING_LEVEL,
        #         format="[Time: %(relativeCreated)6d] " "[Thread: <%(threadName)s>] "
        #         # Uncomment the following line to include the function name in the log
        #         # '%(funcName)s in '
        #         "[File: {%(filename)s:%(lineno)d}] " "%(levelname)s - %(message)s",
        #     )

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
                log.error("IMAGE NOT DISPLAYABLE")
    
    def enqueue_command(self,command):
        log.debug(f"Recieved manually injected command {command}")
        self._my_singleton_received_command_queue.enqueue(command)

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
        self._my_singleton_command_registry.setObject(
            "BladderCommand", BladderCommand()
        )

    def startSystem(self):
        self._my_singleton_thread_manager.new_onetime(
            self._my_singleton_tcp_manager.listenTCP, "ListenTCP", True
        )
        # self._my_singleton_thread_manager.new_periodic(
        #     self._my_singleton_tcp_manager.checkForNewIP,
        #     "CheckNewIP",
        #     config.CHECK_NEW_IP_FROM_PI_FREQUENCY,
        #     True,
        # )
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

def graceful_exit_generator(obj):
    def graceful(sig, frame):
        # loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        # for logger in loggers:
        #     print(logger.handlers)
        log.info("Attempting to exit gracefully")
        stop_motors = {
            "id": int(time.time()),
            "cmd": "SetSpeedCommand",
            "priority": 1,  # , Priority, type int
            "leftSpeed": 0,  # Left speed value, type int
            "rightSpeed": 0,  # Right speed value, type int
            "receivingPort": config.RESPONSE_PORT,
        }
        log.info("Stopping motors")
        obj.enq_command(stop_motors)
        sys.exit(0)
    return graceful

if __name__ == "__main__":
    obj = HSIMaster()
    obj.initializeCommandRegistry()
    # graceful_exit = graceful_exit_generator(obj)
    # atexit.register(graceful_exit)
    # signal.signal(signal.SIGINT, graceful_exit)
    # signal.signal(signal.STGSTP, graceful_exit)


    obj.startSystem()
