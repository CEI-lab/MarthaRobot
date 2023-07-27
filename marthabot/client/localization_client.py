

import atexit
import pickle
from pprint import pp
import socket
import asyncore
import sys
import time
import struct

import logging
log = logging.getlogger(__name__)
import marthabot.configurations.robot_config as config
from marthabot.map.map import Mapper


def getMap():
    pass

def getPoses():
    pass

def sendObject(message, port: int):
    """
    sendObject Send a command dictionary to the robot

    :param message: Dictionary defining a command
    :type message: dict
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to robot
    s.connect((config.HOST, port))

    # send pickled command
    s.send(pickle.dumps(message))
    s.close()

def receiveResponse(port):
    """Wait for and handle response from the robot.

    :param command: Raw command that was input
    :type command: str
    :param port: Port to listen for a response on
    :type port: int
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", port))
    s.listen(5)
    connection, address = s.accept()

    data = []
    # collect all packets
    while True:
        packet = connection.recv(config.BYTES_PER_PACKET)
        if not packet:
            break
        data.append(packet)
    s.close()
    data_arr = pickle.loads(b"".join(data))

    log.debug("raw response data", {"overflow":data_arr})

    
    try:
        if "data" in data_arr:
            log.info("response was: \n")
            log.info(data_arr["data"])

        else:
            log.warning("No 'data' field in response.")
            log.warning(f"Raw response: \n{pp.pformat(data_arr)}")
    except Exception as e:
        log.warning("Problem receiving response",{"overflow":data_arr})
        log.exception(e)
        pass

def multi_cast_message(ip_address, port, message):
    """Send multicast mesage to the RPi and start the appropriate streaming client

    :param ip_address: RPI IP address
    :type ip_address: str
    :param port: Port to send message on
    :type port: int
    :param message: message
    :type message: str
    """
    # send the multicast message
    multicast_group = (ip_address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connections = {}
    try:
        # Send data to the multicast group
        log.info('sending "%s"' % message + str(multicast_group))
        sent = sock.sendto(message.encode(), multicast_group)
        log.debug("message sent")
        # defer waiting for a response using Asyncore
        
        client = MapperClient(config.RASPI_IP_ADDRESS,config.MAPPER_PORT)

        log.debug("entering asyncore loop")
        asyncore.loop(30)

        # Look for responses from all recipients

    except socket.timeout:
        log.warning("timed out, no more responses")
    finally:
        log.info(sys.stderr, "closing socket")
        sock.close()

class MapperClient(asyncore.dispatcher):
    def __init__(self, address, port):
        asyncore.dispatcher.__init__(self, address)
        self.start_time = time.time()
        self.address = address.getsockname()[0]
        self.port = port[1]
        self.buffer = bytearray()
        self.windowName = self.port
        self.remainingBytes = 0
        self.frame_id = 0
        self.map = Mapper("marthabot/map/RhodeMap.yaml",
                        "marthabot/map/MapConfiguration.yaml")
   

    def handle_read(self):
        if self.remainingBytes == 0:
            # get the expected frame size
            recieved = self.recv(4)
            self.frame_length = struct.unpack("<I", recieved)[0]
            self.remainingBytes = self.frame_length

        # request the frame data until the frame is completely in buffer
        data = self.recv(self.remainingBytes)
        self.buffer += data
        self.remainingBytes -= len(data)
        # once the frame is fully recived, process/display it
        if len(self.buffer) == self.frame_length:
            self.display_data()
    def display_data(self):
        # log.debug("imageclient handle_frame")

        # convert the frame from string to numerical data
        fps = 1 / (time.time() - self.start_time)
        log.debug(fps)
        self.start_time = time.time()
        try:
            poses = pickle.loads(self.buffer)
            self.map.plot_map("marthabot/map/map",poses)

        except:
            log.warning("Bad data")
        self.buffer = bytearray()
        self.frame_id += 1

def exit_handler():
    """Function to handle unexpected failures.
    """
    

if __name__ == "__main__":
    # If the program crashses or otherwise closes try to sent a stop command
    atexit.register(exit_handler)

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    log.info("Your Computer Name is:" + hostname)
    log.info("Your Computer IP Address is:" + IPAddr)
    log.info("Target Rover IP Address is:" + config.HOST)
    
    multi_cast_message(config.MC_IP_ADDRESS, config.COMMAND_PORT, "boop")

