"""
Interface to declare the format to be used by all the queues.

CEI-LAB, Cornell University 2019
"""

class QueueInterface(object):

    def __init__(self):
        """
        This method will create the module QueueInterface.

            Inputs:
                None.

            Outputs:
                None.
        """
        pass

    def enqueue(self, valueObject):
        """
        This method will be called to add the passed object in the queue.

            Inputs:
                valueObject : Object to be added in the queue.

            Outputs:
                None

        """
        raise NotImplementedError("QueueInterface.enqueue() not implemented")

    def dequeue(self):
        """
        This method will be called to get the first element in the queue.

            Inputs:
                None

            Outputs:
                valueObject : Object taken out from the queue. None if queue is empty.

        """
        raise NotImplementedError("QueueInterface.dequeue() not implemented")

    def size(self):
        """
        This method will return the size of the queue.

            Inputs:
                None

            Outputs:
                Size of the queue.

        """
        raise NotImplementedError("QueueInterface.dequeue() not implemented")
