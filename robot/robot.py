import robot.configurations as config
import logging
# from thread_manager.ThreadManager import ThreadManager

from robot.controllers.bladder.bladder_controller import BladderController
from robot.controllers.movement.movement_controller import MovementController


class Robot(object):
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Robot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if config.ENABLE_FILE_LOGGING:
            logging.basicConfig(filename=config.LOG_FILENAME.format(config.home),
                                level=config.LOGGING_LEVEL)
        else:
            logging.basicConfig(level=config.LOGGING_LEVEL,
                                format='[Time: %(relativeCreated)6d] '
                                       '[Thread: <%(threadName)s>] '
                                # Uncomment the following line to include the function name in the log
                                # '%(funcName)s in '
                                       '[File: {%(filename)s:%(lineno)d}] '
                                       '%(levelname)s - %(message)s')

        # self._my_singleton_thread_manager = ThreadManager()
        # self._my_singleton_thread_manager.monitor_threads = True

        # self._my_singleton_thread_manager.new_onetime()
        bladderController = BladderController()
        movementController = MovementController()
