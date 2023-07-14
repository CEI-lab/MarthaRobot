import logging
import queue  # This requires python 3

from marthabot.robot.resources.queues.QueueInterface import QueueInterface

"""
A singleton priority queue class. Implemented QueueInterface.
CEI-LAB, Cornell University 2019
"""


class StatusQueue(QueueInterface, object):  # This object is necessary
    """
    Attributes:
        _instance
            Indicates whether there is already an instance of the class. 
            None if the class has not been instantiated.
            Refers to the instance otherwise.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Creates an instance of this class. Only changes _instance once, that is, 
        this class can only be instantiated once.
        Smaller number means higher priority.
        """
        if not cls._instance:
            cls._instance = super(StatusQueue, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initializes the instance created by __new__. Uses PriorityQueue to 
        represent StatusQueue.
        """
        self.my_queue = queue.PriorityQueue()

    def enqueue(self, p, v):
        """
        Put an element into the queue.
        Inputs:
            p: The priority of the element to be enqueued.
            v: The element to be enqueued.
        Outputs:
            None
        """
        self.my_queue.put((p, v))

    def dequeue(self):
        """
        Dequeue an element from the queue.
        Inputs:
            None
        Outputs:
            The element with smallest proirity. If queue is empty then None.
        """
        try:
            res = self.my_queue.get(block=False)
            return res[1]
        except queue.Empty:
            logging.warning(
                "StatusQueue : Dequeuing attempt from an empty queue")
            return None

    def size(self):
        """
        The size of the queue.
        """
        return self.my_queue.qsize()
