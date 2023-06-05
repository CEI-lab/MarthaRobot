import sys
from pathlib import Path

home = str(Path.home())
sys.path.append(home + "/HSI/commands/")
import logging
from robot.commands.CommandInterface import CommandInterface

"""
Implementation of a command registry that will store Command objects
along their respective command names as used in the JSON protocol.

CEI-LAB, Cornell University 2019
"""


class CommandRegistry:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CommandRegistry, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        self._cmd_to_icommand_class = dict()

    def setObject(self, keyCmdString, valueCommandObj):
        """
        This method will be called to add the command name with the respective Command class.

        Inputs:
            keyCmdString : Command name as used in JSON protocol, for the respective command
                passed as value.
            valueCommandObj : Object of a command class that inherits CommandInterface corresponding
                the provided key.

        Outputs:
            None

        """
        if isinstance(valueCommandObj, CommandInterface):
            self._cmd_to_icommand_class[keyCmdString] = valueCommandObj
        else:
            logging.error(
                "CommandRegistry : Not a valid command in setObject operation : Key = "
                + str(keyCmdString)
                + ", Value = "
                + str(valueCommandObj)
            )
            raise TypeError("Not a Command class")

    def getObject(self, keyCmdString):
        """
        This method will be called to add the command name with the respective Command class.

        Inputs:
            keyCmdString : Command name as used in JSON protocol, for the respective command
                passed as value.

        Outputs:
            Object of a command class that inherits CommandInterface corresponding
                the provided key. If there is no entry along the key, then return None.

        """
        if keyCmdString in self._cmd_to_icommand_class:
            return self._cmd_to_icommand_class[keyCmdString]
        else:
            logging.warning(
                "CommandRegistry : No command in the registry with the name : "
                + str(keyCmdString)
            )
            return None
