"""
Implementation of a command executer that will execute a command extracted from
command queue.

CEI-LAB, Cornell University 2019
"""
import sys
from multiprocessing import Lock
from pathlib import Path
import time

home = str(Path.home())
sys.path.append(home + "/HSI/resources/registries")
sys.path.append(home + "/HSI/resources/queues")

import logging


class CommandExecuter:
    _instance = None
    _lock = Lock()

    def __new__(cls, comque, statque, comreg, comevent, statevent):
        """Enforces singleton object by creating an instance of this class.
        Only changes _instance once, that is, this class can only be instantiated once.
        Smaller number means higher priority.

        TODO remove extra arguments
        :param comque: These seem to no longer be in use....
        :type comque: _type_
        :param statque: These seem to no longer be in use....
        :type statque: _type_
        :param comreg: These seem to no longer be in use....
        :type comreg: _type_
        :param comevent: These seem to no longer be in use....
        :type comevent: _type_
        :param statevent: These seem to no longer be in use....
        :type statevent: _type_
        :return: These seem to no longer be in use....
        :rtype: _type_
        """

        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, comque, statque, comreg, comevent, statevent):
        self._my_command_queue = comque  # Command queue
        self._my_command_registry = comreg  # Command registry
        self._my_status_queue = statque  # Status queue
        self._my_command_event = comevent  # Command event
        self._my_status_event = statevent  # Status event

    def statusResponseCallback(self, json):
        """
        Enqueue a command to the status queue.

        :param json: The json object to be enqueued.
        :type json: dictionary

        :raises ValueError: If the priority contained in json is not a number.
        """
        self._lock.acquire()
        pri = json.get("priority")
        if pri is None:
            json["response"] = "PRIORITY_FIELD_MISSING"
            self._my_status_queue.enqueue(1, json)
            logging.error(
                "CommandExecuter : No priority field in the status JSON object"
            )
        else:
            if json.get("id") is None:
                json["id"] = -1
                json["response"] = "ID_FIELD_MISSING"
            # Will raise error if priority is not an int
            self._my_status_queue.enqueue(int(pri), json)
        self._my_status_event.set()
        self._lock.release()

    def _parse_key(self, json):
        """
        Get the command name from json object.
        Imputs:
            json: The json object to be parsed.
        Outputs:
            The command name contained in json. If json doesn't contain the
            command name, then returns None.
        """
        return json.get("cmd")

    def processCommand(self, json):
        """
        Execute the command contained in the json object.


        :param json: The json object contains an command.
        :type json: json
        """
        logging.debug("CommandExecuter : Received JSON object" + str(json))
        key = self._parse_key(json)
        if key is not None:
            cmd = self._my_command_registry.getObject(key)
            if cmd is not None:
                cmd.execute(self.statusResponseCallback, json)
            else:
                logging.error(
                    "CommandExecuter : No entry in CommandRegistry for " + str(key)
                )
        else:
            logging.error("CommandExecuter : No command name in the JSON object")

    def checkForCommand(self):
        """
        Watch for (and handle) new commands on the command queue.
        """
        while True:
            self._my_command_event.wait()
            if self._my_command_queue.size() > 0:
                nextCommand = (
                    self._my_command_queue.dequeue()
                )  # remove from the command queue
                self.processCommand(nextCommand)
            else:
                self._my_command_event.clear()
