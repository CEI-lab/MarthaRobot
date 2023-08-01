import atexit
import asyncore
import pickle
from pprint import pp
import logging

# logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
# logging.root.setLevel(logging.WARNING)
import socket
import asyncore
import sys
import time
import struct
import asyncio
from matplotlib import pyplot as plt


import asyncio_dgram as aiod

log = logging.getLogger(__name__)
from configurations import robot_config as config
from map.mapper import Mapper

# plt.ion()
# plt.ion()


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

    log.debug("raw response data", {"overflow": data_arr})

    try:
        if "data" in data_arr:
            log.info("response was: \n")
            log.info(data_arr["data"])

        else:
            log.warning("No 'data' field in response.")
            log.warning(f"Raw response: \n{pp.pformat(data_arr)}")
    except Exception as e:
        log.warning("Problem receiving response", {"overflow": data_arr})
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
    robot_address = (ip_address, port)
    # multicast_group = ip_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = {}
    try:
        # Send data to the multicast group
        log.info(f"Sending {message} to {str(robot_address)}")
        sent = sock.sendto(message.encode(), robot_address)
        log.debug("message sent")
        # defer waiting for a response using Asyncore

        client = MapperClient()

        log.debug("entering asyncore loop")
        asyncore.loop(30)

        # Look for responses from all recipients

    except socket.timeout:
        log.warning("timed out, no more responses")
    except Exception as e:
        log.exception(e)
    finally:
        log.info("closing socket")
        sock.close()


class AsyncoreClientUDP(asyncore.dispatcher):
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.buffer = "".encode()

        # Network Connection Magic!
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(("", port))  # bind to all interfaces and a "random" free port.
        log.info("Connecting...")

    # Once a "connection" is made do this stuff.
    def handle_connect(self):
        log.info("Connected")

    # If a "connection" is closed do this stuff.
    def handle_close(self):
        log.info("Closing socket")
        self.close()

    # If a message has arrived, process it.
    def handle_read(self):
        data, addr = self.recv(2048)
        log.info(f"Recieved: {data}")

    def writeable(self):
        return len(self.buffer) > 0

    # Actually sends the message if there was something in the buffer.
    def handle_write(self):
        log.debug(f"Buffer:  {self.buffer}")
        sent = self.sendto(self.buffer, (self.server, self.port))
        log.debug(f"Sent {sent}")
        self.buffer = self.buffer[sent:]
        log.debug(f"Updated: {self.buffer}")


class UDPClient(asyncore.dispatcher):
    def __init__(self, server, source):
        asyncore.dispatcher.__init__(self, server)
        asyncore.dispatcher.__init__(self)
        self.start_time = time.time()
        self.address = server.getsockname()[0]
        self.port = source[1]
        self.buffer = bytearray()
        self.windowName = self.port
        # open cv window which is unique to the port
        log.info("Opening window")
        self.remainingBytes = 0
        self.frame_id = 0
        log.info("window setup complete")

    def handle_read(self):
        log.debug("udp handle read")
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
        log.debug("udp display_data")

        # convert the frame from string to numerical data
        fps = 1 / (time.time() - self.start_time)
        log.debug(fps)
        self.start_time = time.time()
        try:
            poses = pickle.loads(self.buffer)
            self.map.plot_map("marthabot/map/map", poses)

        except:
            log.warning("Bad data")
        self.buffer = bytearray()
        self.frame_id += 1

    def readable(self):
        return True


class MapperClient(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.map = Mapper("map/RhodeMap.yaml", "map/MapConfiguration.yaml")
        self.start_time = time.time()
        self.server_address = ("", config.MAPPER_PORT)
        self.create_socket(
            socket.AF_INET, socket.SOCK_STREAM
        )  # TODO consider changing to UDP
        self.socket.settimeout(5)

        self.bind(self.server_address)
        self.listen(5)

    def writable(self):
        log.debug("Confirmed not writable")
        return False  # don't want write notifies

    def readable(self):
        log.debug("Confirmed readable")
        return True

    def handle_connect(self):
        print("connection recvied")

    def handle_accept(self):
        log.debug("pose handle_accept")
        pair = self.accept()
        # print(self.recv(10))
        if pair is not None:
            sock, addr = pair
            log.info(f"Incoming connection from {repr(addr)}")
            # when a connection is attempted, delegate image receival to base client
            handler = UDPClient(sock, addr)


def exit_handler():
    """Function to handle unexpected failures."""


best_time = 0


async def udp_reciever(port):
    stream = await aiod.bind((config.CLIENT_IP_ADDRESS, port))
    log.info(f"Receiving on {stream.sockname}")
    global best_time
    plt.ion()
    fig = plt.figure()
    m = Mapper(
        "C:/Users/63nem/Documents/MarthaRobot/marthabot/map/RhodeMap.yaml",
        "C:/Users/63nem/Documents/MarthaRobot/marthabot/map/MapConfiguration.yaml",
    )
    print("plotted map")
    m.plot_map(fig)
    plt.show()
    plt.draw()
    plt.pause(0.001)

    print("showing map")

    while True:
        data, remote_addr = await stream.recv()

        data = pickle.loads(data)

        t = data[0]
        poses = data[1]

        log.info(f"Recieved new poses at  {time.time()}")
        log.info(f"{poses}")

        if t > best_time:
            best_time = t
            m.plot_poses(fig, poses)
            # for e in data:
            #     t, x, y, z, theta, ci = data
            plt.draw()
            plt.pause(0.01)

        else:
            log.warning("Out of order message ignored")


async def udp_dispatcher(port):
    stream = await aiod.connect((config.RASPI_IP_ADDRESS, port))
    log.info(f"Sending on {stream.sockname}")

    while True:
        stream = await aiod.connect((config.RASPI_IP_ADDRESS, port))
        inp = input("Enter message: \n")
        await stream.send(inp.encode())
        # stream.socket.sendall()
        log.info(f"Sent: {inp} on port {port}")
        stream.close()


def main():
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    log.info("Your Computer Name is:" + hostname)
    log.info("Your Computer IP Address is:" + IPAddr)
    log.info("Target Rover IP Address is:" + config.HOST)

    # multi_cast_message(config.RASPI_IP_ADDRESS, config.MAPPER_PORT, "boop")

    # connection = AsyncoreClientUDP(config.RASPI_IP_ADDRESS, config.MAPPER_PORT)

    # try:
    #     while True:
    #         print(connection.buffer)
    #         connection.buffer += input(" Chat > ").encode()
    #         asyncore.loop(count=10)

    # except KeyboardInterrupt:
    #     log.warning("Closing due to keyboard interrupt")
    # except Exception as e:
    #     log.error("Issue running server")
    #     log.exception(e)

    loop = asyncio.get_event_loop()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            udp_reciever(config.MAPPER_PORT),
            # udp_dispatcher(config.MAPPER_PORT),
        )
    )


if __name__ == "__main__":
    # If the program crashses or otherwise closes try to sent a stop command
    atexit.register(exit_handler)
    # asyncio.run(main())

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            udp_reciever(config.MAPPER_PORT),
            udp_dispatcher(config.MAPPER_PORT),
        )
    )
