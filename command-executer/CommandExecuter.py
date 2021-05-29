import sys
from multiprocessing import Lock
from pathlib import Path
import time

home = str(Path.home())
sys.path.append(home + "/HSI/resources/registries")
sys.path.append(home + "/HSI/resources/queues")

import logging

"""
Implementation of a command executer that will execute a command extracted from
command queue.

CEI-LAB, Cornell University 2019
"""


class CommandExecuter:

    _instance = None
    _lock = Lock()

    def __new__(cls, comque, statque, comreg):
        """
        Creates an instance of this class. Only changes _instance once, that is,
        this class can only be instantiated once.
        Smaller number means higher priority.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, comque, statque, comreg):
        self._my_command_queue = comque  # command queue
        self._my_command_registry = comreg  # command registry
        self._my_status_queue = statque  # status queue

    def statusResponseCallback(self, json):
        """
        Enqueue current json to the status queue.
        Inputs:
            json: The json object to be enqueued.
        Outputs:
            None
        Raises:
            ValueError if the priority contained in json is not a number.
        """
        self._lock.acquire()
        pri = json.get("priority")
        if pri is None:
            json["response"] = "PRIORITY_FIELD_MISSING"
            self._my_status_queue.enqueue(1, json)
            logging.error('CommandExecuter : No priority field in the status JSON object')
        else:
            if json.get("id") is None:
                json["id"] = -1
                json["response"] = "ID_FIELD_MISSING"
            # Will raise error if priority is not an int
            self._my_status_queue.enqueue(int(pri), json)
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
        Inputs:
            json: The json object contains an command.
        Outputs:
            None.
        """
        logging.debug('CommandExecuter : Received JSON object' + str(json))
        key = self._parse_key(json)
        if key is not None:
            cmd = self._my_command_registry.getObject(key)
            if cmd is not None:
                cmd.execute(self.statusResponseCallback, json)
            else:
                logging.error('CommandExecuter : No entry in CommandRegistry for ' + str(key))
        else:
            logging.error('CommandExecuter : No command name in the JSON object')
    def checkForCommand(self):
        """
        Check whether there is an command avaliable in the command queue.
        Inputs:
            None.
        Outputs:
            None.
        """
        while True:
            # time.sleep(0.005)
            # begin_time = time.time()
            # There is at least one command in the command queue.
            if self._my_command_queue.size() > 0:
                nextCommand = self._my_command_queue.dequeue()  # remove from the command queue
                self.processCommand(nextCommand)
                # print("fr is {}".format(1/(time.time()-begin_time)))
