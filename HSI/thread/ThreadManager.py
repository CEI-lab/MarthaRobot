import threading
import logging
import traceback
from threading import Thread
import time
import sys

"""
This class can be used to start new threads and log messages messages. It is important to note that in any code that 
leverages this thread manager should use the method "logging.debug()" instead of print. This allows messages to be 
displayed with thread and time info. (Legacy Code - Only manually tested and reviewed)

CEI-LAB, Cornell University 2019
"""


class ThreadManager(Thread):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ThreadManager, cls).__new__(
                cls, *args, **kwargs)

        return cls._instance

    def __init__(self):

        # Call parent constructor
        Thread.__init__(self)
        self.daemon = True
        self.name = 'Thread Manager'

        # Global variables for storing theads and thread counts
        self.periodic_threads = []
        self.onetime_threads = []
        self.periodic_count = 0
        self.onetime_count = 0

        # time string for recording time in logging filename
        # timestr = time.strftime("%Y%m%d-%H:%M:%S")

        # Parameters for printing thread status
        #logging.basicConfig(level=logging.DEBUG,
        #                    format='[Time: %(relativeCreated)6d] ' \
        #                           '[Thread: <%(threadName)s>] '
        #                    # Uncomment the following line to include the function name in the log
        #                    # '%(funcName)s in '
        #                           '[File: {%(filename)s:%(lineno)d}] '
        #                           '%(levelname)s - %(message)s')
        self.monitor_threads = False
        self.monitor_debug_period = 3.
        self.alive_count = 0

    # filehandler = logging.FileHandler('logging_'+timestr+'.log')
    # logger = logging.getLogger(__name__)
    # logger.addHandler(filehandler)

    def run(self):

        # This is the method that is called when the user calls the "start()" method.
        # Its primary task is to monitor if the child threads are active and report
        # thread status, It also is responsible for signaling the termination of the
        # Thread Manager once all children threads have died.

        if not self.monitor_threads:
            logging.debug('Thread Monitoring disabled for Thread Manager')

        # This block of code periodically monitors the status of each child thread
        while self.alive_count > 0:

            self.alive_count = sum([t.isAlive() for t in self.periodic_threads]) + sum(
                [t.isAlive() for t in self.onetime_threads])

            if self.monitor_threads:
                logging.debug('Number of active child threads: ' + str(self.alive_count))
                for t in threading.enumerate():
                    logging.debug(t)

            time.sleep(self.monitor_debug_period)

    def stop_periodic_thread(self, thread_name):

        # This method stops a periodic thread with a given name

        found = False

        for t in self.periodic_threads:
            if t.name == thread_name:
                t.stop_thread()
                found = True

        if not found:
            logging.error('No periodic child thread with name "' + thread_name + '" found. Unable to stop thread')

    def resume_periodic_thread(self, thread_name):

        # This method resumes a periodic thread with a given name

        found = False

        for t in self.periodic_threads:
            if t.name == thread_name:
                t.resume_thread()
                found = True

        if not found:
            logging.error('No periodic child thread with name "' + thread_name + '" found. Unable to resume thread')

    def run_while_active(self):

        # This method should only be called from the main thread in order
        # to avoid the program becoming unresponsive

        while self.isAlive(): time.sleep(.1)

    def set_monitor_debug_frequency(self, frequency):

        # Update monitor period
        self.monitor_debug_period = 1. / frequency

    def new_periodic(self, function, thread_name, frequency, daemonic=True, *argv):

        # This function is a factory that generates a new periodic thread. Threads
        # should be set to daemonic to avoid the an unresponsive program (unless
        # you don't want the thread to end with the main thread dies).

        # Create new periodic thread
        per_thread = PeriodicThread(function, frequency, *argv)
        per_thread.setName(thread_name)
        per_thread.daemon = daemonic

        # Add thread to global monitoring list
        self.periodic_count = self.periodic_count + 1
        self.alive_count = self.alive_count + 1
        self.periodic_threads.append(per_thread)

    def new_onetime(self, function, thread_name, daemonic=True, *argv):

        # This function is a factory that generates a new thread. Threads
        # should be set to daemonic to avoid the an unresponsive program (unless
        # you don't want the thread to end with the main thread dies).

        # Create new onetime thread
        ot_thread = OnetimeThread(function, *argv)
        ot_thread.setName(thread_name)
        ot_thread.daemon = daemonic

        # Add thread to global monitoring list
        self.onetime_count = self.onetime_count + 1
        self.alive_count = self.alive_count + 1
        self.onetime_threads.append(ot_thread)

    def start_all(self):

        # This method calls "start()" for each thread in the global monitoring lists

        for t in self.periodic_threads:
            t.start()

        for t in self.onetime_threads:
            t.start()

    def join_all(self):

        # This method calls "join()" for each thread in the global monitoring lists

        for t in self.periodic_threads:
            t.join()

        for t in self.onetime_threads:
            t.join()

    def start_by_name(self, name):

        # This method calls "start()" for a thread with a specific name

        for t in self.periodic_threads:
            if t.name == name:
                t.start()

        for t in self.onetime_threads:
            if t.name == name:
                t.start()

    def join_by_name(self, name):

        # This method calls "join()" for a thread with a specific name

        for t in self.periodic_threads:
            if t.name == name:
                t.join()

        for t in self.onetime_threads:
            if t.name == name:
                t.join()


"""
This is a helper class that executes a target method in a new thread. It helps the ThreadManager create new threads.

CEI-LAB, Cornell University 2019
"""


class OnetimeThread(Thread):
    def __init__(self, function, *argv):

        Thread.__init__(self)
        self.args = argv
        self.function = function

    def run(self):

        try:
            self.function(*self.args)
        except:
            logging.error('OnetimeThread Error: ')
            logging.error(traceback.format_exc())


"""
This is a helper class that periodically executes a target method in a new thread. It helps the ThreadManager create 
new threads.

CEI-LAB, Cornell University 2019
"""


class PeriodicThread(Thread):

    def __init__(self, function, frequency, *argv):

        # Call parent constructor
        Thread.__init__(self)

        # Set parameters for periodic execution
        self.frequency = frequency
        self.period = 1.0 / frequency

        # Method and arguments
        self.function = function
        self.args = argv
        self.stop = False

    def run(self):

        while not self.stop:
            # Time exicution of target function in order to determin remaining wait time
            start_time = time.time()
            try:
                self.function(*self.args)
            except:
                logging.error('PeriodicThread Error: ' )
                logging.error(traceback.format_exc())

            # If execution time is greater than wait time, don't wait.
            exicution_time = time.time() - start_time
            if exicution_time > 0:
                time.sleep(self.period)

    def stop_thread(self):

        self.stop = True

    def resume_thread(self):

        self.stop = False
        self.run()
