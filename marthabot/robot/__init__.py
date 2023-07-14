"""
Code related to controlling the robot.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from marthabot.utils.custom_logger import setup_logging
setup_logging(__name__)

from marthabot.robot import commands
from marthabot.robot import tcp_manager 
from marthabot.robot import thread_manager

# __all__ = ["resources", "commands", "tcp_manager", "thread_manager"]

