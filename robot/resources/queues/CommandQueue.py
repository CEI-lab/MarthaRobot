import sys
from pathlib import Path

from robot.resources.queues.QueueInterface import QueueInterface
import queue
import logging

"""
Interface to declare the format to be used by all the queues.

CEI-LAB, Cornell University 2019
"""


class CommandQueue(QueueInterface):
    """

    A singleton queue to hold commands.

    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """

        This method ensures the CommandQueue is singelton.


        :return: An singleton instance of CommandQueue
        :rtype: :class:`robot.resources.queues.CommandQueue.CommandQueue`
        """

        if not cls._instance:
            cls._instance = super(CommandQueue, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        """This method will create a new queue in singelton."""

        self.my_queue = queue.Queue()

        # queue_object.queue will return copy of your queue in a deque object which you can then use the slices of.
        # which is not synchronized with the original queue, but will allow you to peek at the queue at the time of the
        # copy.
        self.my_dque = self.my_queue.queue

    def enqueue(self, valueObject):
        """This method will be called to add the passed object in the queue.


        :param valueObject: Object to be added in the queue.
        :type valueObject:
        """

        self.my_queue.put(valueObject)

    def dequeue(self):
        """This method will be called to get the first element in the queue.


        :return: Next command in queue. None if queue is empty.
        :rtype:
        """

        try:
            return self.my_queue.get(block=False)
        except queue.Empty:
            logging.warning("CommandQueue : Dequeuing attempt from an empty queue")
            return None

    def remove(self, keyString):
        """Remove commands with the key equals to keyString.

        TODO Seems to not be in use, and docstring is not clear

        :param keyString: keyString for comparing each key in every dictionary.

        :type keyString: str
        """

        for queue_index in range(self.my_queue.qsize()):
            if list(self.my_dque[queue_index].keys())[0] == keyString:
                self.my_dque[queue_index].clear()

    def size(self):
        """This method will return the size of the queue even with empty dictionaries.


        :return: size of queue
        :rtype: int
        """

        return self.my_queue.qsize()

    def realSize(self):
        """
        ONLY FOR THE UNITTEST
        This method will return the real size of the queue.
        For instacne, an empty dictionary wouldn't considered a part of the queue.

        :return: size of queue
        :rtype: int
        """
        tmp_realSize = 0
        for queue_index in range(self.my_queue.qsize()):
            if self.my_dque[queue_index] != {}:
                tmp_realSize += 1
        return tmp_realSize
