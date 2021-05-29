from pathlib import Path
import sys

home = str(Path.home())
sys.path.append(home + "/HSI/resources/queues/")

from StatusQueue import StatusQueue
import unittest

"""
Tests for StatusQueue.
"""


class StatusQueueTests(unittest.TestCase):

    def setUp(self):
        self.sqObj = StatusQueue()

    def tearDown(self):
        self.sqObj = None

    def test_DequeueOnEmptyQueue(self):
        """
        Test whether dequeue on an empty queue returns None.
        """
        self.assertIsNone(self.sqObj.dequeue())

    def test_SizeAndDequeue(self):
        """
        Test whether dequeue() returns elements based on priority, that is, 
        returns the priority with smallest number first.
        """
        self.sqObj.enqueue(3, "s")
        self.sqObj.enqueue(1, "h")
        self.sqObj.enqueue(5, "i")
        self.assertEqual(self.sqObj.size(), 3)
        self.assertEqual(self.sqObj.dequeue(), "h")
        self.assertEqual(self.sqObj.size(), 2)
        self.assertEqual(self.sqObj.dequeue(), "s")
        self.assertEqual(self.sqObj.size(), 1)
        self.assertEqual(self.sqObj.dequeue(), "i")
        self.assertEqual(self.sqObj.size(), 0)

    def test_SingletonClassCheck(self):
        """
        Test whether StatusQueue is a singleton class.
        """
        # Creating a new object, but since the class is expected to be singleton
        # It will be the same object
        obj = StatusQueue()
        self.assertEqual(self.sqObj, obj)


if __name__ == '__main__':
    unittest.main()
