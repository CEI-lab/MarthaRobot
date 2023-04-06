from pathlib import Path
import sys

home = str(Path.home())
sys.path.append(home + "/HSI/commands/")
sys.path.append(home + "/HSI/resources/registries/")

from CommandRegistry import CommandRegistry
from CommandInterface import CommandInterface
import unittest

"""
A temporary Command class used for testing.
"""


class TempCommand(CommandInterface):

    def execute(self, responseStatusCallback, jsonObject):
        pass

    def create(self):
        pass


"""
Test cases for CommandRegistry class
"""


class TestCommandRegistryTests(unittest.TestCase):

    def setUp(self):
        self.cmdRegObj = CommandRegistry()

    def tearDown(self):
        self.cmdRegObj = None

    def test_GetObjectForKeyNotExist(self):
        """
        Test whether getObject() function returns a None if the key doesn't exist in the registry.
        """
        self.assertEqual(self.cmdRegObj.getObject("UnknownKey"), None)

    def test_SetAndGetObjectForValidCommandKeyObject(self):
        """
        Test whether setObject() and getObject() functions work as expected with a valid Command object.
        """
        obj = TempCommand()
        self.cmdRegObj.setObject("Key", obj)
        self.assertEqual(self.cmdRegObj.getObject("Key"), obj)

    def test_SetObjectForInvalidKeyObjectRaisesError(self):
        """
        Test whether setObject() raises an error if we pass an invalid Command object.
        """
        obj = 123
        with self.assertRaises(TypeError):
            self.cmdRegObj.setObject("Key", obj)

    def test_SingletonClassCheck(self):
        """
        Test whether CommandRegistry is a singleton class.
        """
        # Creating a new object, but since the class is expected to be singleton
        # It will be the same object
        obj = CommandRegistry()
        self.assertEqual(self.cmdRegObj, obj)
