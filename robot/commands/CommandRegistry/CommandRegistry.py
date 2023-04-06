import sys
from pathlib import Path

home = str(Path.home())
sys.path.append(home + "/HSI/commands/")
import logging
from robot.commands.CommandInterface import CommandInterface
from robot.commands.CommandRegistry.CommandRegistryInterface import CommandRegistryInterface

"""
Implementation of a command registry (CommandRegistryInterface) that will store Command objects
along their respective command names as used in the JSON protocol.

CEI-LAB, Cornell University 2019
"""


class CommandRegistry(CommandRegistryInterface):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CommandRegistry, cls).__new__(
                cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        self._cmd_to_icommand_class = dict()

    def setObject(self, keyCmdString, valueCommandObj):
        if isinstance(valueCommandObj, CommandInterface):
            self._cmd_to_icommand_class[keyCmdString] = valueCommandObj
        else:
            logging.error("CommandRegistry : Not a valid command in setObject operation : Key = " + str(keyCmdString)
                          + ", Value = " + str(valueCommandObj))
            raise TypeError("Not a Command class")

    def getObject(self, keyCmdString):
        if keyCmdString in self._cmd_to_icommand_class:
            return self._cmd_to_icommand_class[keyCmdString]
        else:
            logging.warning(
                "CommandRegistry : No command in the registry with the name : " + str(keyCmdString))
            return None
