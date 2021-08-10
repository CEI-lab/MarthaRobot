from pathlib import Path
import sys

home = str(Path.home())
sys.path.append(home + "/HSI/resources/queues/")
from CommandQueue import CommandQueue
import unittest

"""
Test cases for CommandQueue class
"""


class CommandQueueTests(unittest.TestCase):

    def setUp(self):
        """
        set up the test object for each unittests. 
        """
        self.cmdQueObj = CommandQueue()

    def tearDown(self):
        """
        Reset the object to none after the unittests. 
        """
        self.cmdQueObj = None

    def test_SingletonClassCheck(self):
        """
        Test whether the CommandQueue is a singleton class.
        """
        # Creating another CommandQueue class since the class is expected to be singleton
        # The new CommandQueue object should be the same. 
        tmpCmdQueObj = CommandQueue()
        self.assertEqual(self.cmdQueObj, tmpCmdQueObj)

    def test_size(self):
        """
        Test whether the size are responding correctly. 
        """
        self.assertEqual(self.cmdQueObj.size(), 0)

        queue_size = 3
        for i in range(queue_size):
            self.cmdQueObj.enqueue({'setSpeed': (i, i)})
        self.assertEqual(self.cmdQueObj.size(), queue_size)

    def test_enqueue(self):
        """
        Test whether we can enqueue the CommandQueue.
        """
        self.assertEqual(self.cmdQueObj.size(), 0)

        enqueue_size = 3
        for i in range(enqueue_size):
            self.cmdQueObj.enqueue({'setSpeed': (i, i)})
        self.assertEqual(self.cmdQueObj.size(), enqueue_size)

    def test_dequeue(self):
        """
        Test whether we can dequeue the CommandQueue.
        """
        self.assertEqual(self.cmdQueObj.size(), 0)

        enqueue_size = 6
        for i in range(enqueue_size):
            self.cmdQueObj.enqueue({'setSpeed': (i, i)})

        self.assertEqual(self.cmdQueObj.size(), enqueue_size)

        dequeue_size = 3
        for i in range(dequeue_size):
            self.cmdQueObj.dequeue()

        self.assertEqual(self.cmdQueObj.size(), enqueue_size - dequeue_size)

    def test_removeKeys(self):
        """
        Test whether the specific key can be removed. 
        """
        self.assertEqual(self.cmdQueObj.size(), 0)

        enqueue_setspeed_size = 6
        for i in range(enqueue_setspeed_size):
            self.cmdQueObj.enqueue({'setSpeed': (i, i)})

        self.assertEqual(self.cmdQueObj.size(), enqueue_setspeed_size)

        enqueue_skewimage_size = 3
        for i in range(enqueue_skewimage_size):
            self.cmdQueObj.enqueue({'skewImage': True})

        self.assertEqual(self.cmdQueObj.size(), enqueue_setspeed_size + enqueue_skewimage_size)

        self.cmdQueObj.remove('setSpeed')
        self.assertEqual(self.cmdQueObj.realSize(), enqueue_skewimage_size)


if __name__ == '__main__':
    unittest.main()
