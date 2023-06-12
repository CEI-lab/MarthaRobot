import unittest
import socket

from pathlib import Path
import sys

home = str(Path.home())
sys.path.append(home + "/HSI/tcp-manager")
sys.path.append(home + "/HSI/resources/queues")

from TCPManager import TCPManager
from CommandQueue import CommandQueue
from StatusQueue import StatusQueue


"""
Test cases for TCPManager class
"""

_test_json_object = {
    "Id": "<timestamp>",
    "Commands": [
        {
            "cmd": "SetSpeed",
            "priority": 1,
            "replaceOldCommands": False,  # Remove similar commands
            "leftSpeed": 1,  # 1 m/sec
            "rightSpeed": 1,  # 1 m/sec
        }
    ],
}


class TCPManagerTests(unittest.TestCase):
    def setUp(self):
        """
        Set up the test object for each unittests.
        """
        self.cmdQueObj = CommandQueue()
        self.sttQueObj = StatusQueue()
        self.tcpManagerObj = TCPManager(self.cmdQueObj, self.sttQueObj)

    def tearDown(self):
        """
        Reset the object to none after the unittests.
        """
        self.tcpmanagerObj = None

    def test_SingletonClassCheck(self):
        """
        Test whether the TCPManager is a singleton class.
        """
        # Creating another CommandQueue class since the class is expected to be singleton
        # The new CommandQueue object should be the same.

        # Create a new tcpmanager for singleton test
        tmpCmdQueObj = CommandQueue
        tmpSttQueObj = StatusQueue
        tmpTcpMangerObj = TCPManager(tmpCmdQueObj, tmpSttQueObj)

        self.assertEqual(self.tcpManagerObj, tmpTcpMangerObj)


if __name__ == "__main__":
    unittest.main()
