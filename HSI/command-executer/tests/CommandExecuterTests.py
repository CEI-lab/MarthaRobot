from pathlib import Path
import sys

home = str(Path.home())
sys.path.append(home + "/HSI/commands/")
sys.path.append(home + "/HSI/command-executer/")
sys.path.append(home + "/HSI/resources/")
sys.path.append(home + "/HSI/resources/queues/")
sys.path.append(home + "/HSI/resources/registries/")

from CommandExecuter import CommandExecuter
from CommandRegistry import CommandRegistry
from CommandInterface import CommandInterface
from StatusQueue import StatusQueue
from CommandQueue import CommandQueue
from unittest import mock
import unittest

"""
Tests for CommandExecuter.
"""

j1 = {
    "cmd": "SetSpeed",
    "priority": "#",
    "replaceOldCommands": True,
    "leftSpeed": 1,  # 1 m/sec
    "rightSpeed": 1,  # 1 m/sec
}
j2 = {
    "cmd": "SkewImage",
    "priority": 8,
    "srcFileName": "png",  # Folders are fixed
    "destFileName": "png",  # Folders are fixed
    "overwriteDestFileIfExists": "true"

}
j3 = {
    "cmd": "StopVideoRecording"
}
j4 = {
    "cmd": "StopVideoRecording",
    "priority": 5,
}


class CommandExecuterTests(unittest.TestCase):
    def setUp(self):
        """
        Set up the test object for each unittests.
        """
        self._command_queue_obj = CommandQueue()
        self._status_queue_obj = StatusQueue()
        self._command_registry_obj = CommandRegistry()

        self._command_executer_obj = CommandExecuter(self._command_queue_obj, self._status_queue_obj,
                                                     self._command_registry_obj)

    def tearDown(self):
        """
        Tear down up the test object for each unittests.
        """

        self._command_executer_obj = None
        self._command_queue_obj = None
        self._status_queue_obj = None
        self._command_registry_obj = None

    def test_statusResponseCallback(self):
        """
        Test whether statusResponseCallback raises ValueError if the priority
        is not a number or enqueue the json to the status queue.
        """
        self.assertRaises(ValueError, self._command_executer_obj.statusResponseCallback, j1)
        self._command_executer_obj.statusResponseCallback(j2)
        self._command_executer_obj.statusResponseCallback(j4)
        self.assertEqual(self._status_queue_obj.dequeue(), j4)
        self.assertEqual(self._status_queue_obj.dequeue(), j2)

    def test_parse_key(self):
        """
        Test whether _parse_key gets the command name.
        """
        self.assertEqual(self._command_executer_obj._parse_key(j1), 'SetSpeed')
        self.assertEqual(self._command_executer_obj._parse_key(j2), 'SkewImage')
        self.assertEqual(self._command_executer_obj._parse_key(j3), 'StopVideoRecording')

    def test_ProcessCommandForValidJSON(self):
        """
        Test whether the execute() is executed if the json is valid.
        """
        com = CommandInterface()  # Didn't find the implementation of CommandInterface
        com.execute = mock.Mock()
        self._command_registry_obj.setObject("SetSpeed", com)
        self._command_executer_obj.processCommand(j1)
        com.execute.assert_called_once()

    def test_ProcessCommandForInvalidJSON(self):
        """
        Test whether the execute() is executed if the json is not valid.
        """
        com = CommandInterface()  # Didn't find the implementation of CommandInterface
        com.execute = mock.Mock()
        self._command_registry_obj.setObject("Set", com)
        self._command_executer_obj.processCommand(j1)
        com.execute.assert_not_called()

    def test_SingletonClassCheck(self):
        """
        Test whether CommandExecuter is a singleton class.
        """
        # Creating a new object, but since the class is expected to be singleton
        # It will be the same object
        obj = CommandExecuter(CommandQueue(), StatusQueue(), CommandRegistry())
        self.assertEqual(self._command_executer_obj, obj)


if __name__ == '__main__':
    unittest.main()
