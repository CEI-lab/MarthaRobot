import sys
import getopt
import asyncore
import numpy as np
import pickle
import socket
import struct
import cv2
import time
import logging as log
import client.Configurations as config

mode = ""
port = ""


def main(argv):
    """Entry point for the streaming client, connects and displays output to/from the RPi.
    prompts user for which camera to stream from.

    :param argv: not currently used
    :type argv: _type_
    """
    while mode not in config.ports.keys["tof", "rs", "ext"]:
        mode = input("Select mode (tof, rs, ext)")
    port = config.ports[mode]

    # Send a message to get things started
    multi_cast_message(config.MC_IP_ADDRESS, port, "boop")


# UDP client for each camera server


class ImageClient(asyncore.dispatcher):
    def __init__(self, server, source):
        asyncore.dispatcher.__init__(self, server)
        self.start_time = time.time()
        self.address = server.getsockname()[0]
        self.port = source[1]
        self.buffer = bytearray()
        self.windowName = self.port
        # open cv window which is unique to the port
        log.info("Opening window")
        if mode == "rs":
            cv2.namedWindow("depth" + str(self.windowName))
            cv2.namedWindow("color" + str(self.windowName))
        elif mode == "ext":
            cv2.namedWindow("ExtCam" + str(self.windowName))
        self.remainingBytes = 0
        self.frame_id = 0
        log.info("window setup complete")

    def handle_read(self):
        # log.debug("imageclient handle_read")
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
            self.handle_frame()

    def handle_frame(self):
        # log.debug("imageclient handle_frame")

        # convert the frame from string to numerical data
        fps = 1 / (time.time() - self.start_time)
        log.debug(fps)
        self.start_time = time.time()
        try:
            imdata = pickle.loads(self.buffer)
            if mode == "rs":
                depth = imdata[:, 0:320]
                color = np.clip(imdata[:, 320:640], 0, 256).astype("uint8")
                bigDepth = cv2.resize(
                    depth, (0, 0), fx=2, fy=2, interpolation=cv2.INTER_NEAREST
                )
                bigDepth = np.clip(bigDepth, 0, 5000)
                bigDepth = cv2.applyColorMap(
                    (bigDepth / (5000 / 256)).astype(np.uint8), cv2.COLORMAP_RAINBOW
                )
                cv2.imshow(
                    "depth" + str(self.windowName), cv2.resize(bigDepth, (544, 408))
                )
                cv2.imshow(
                    "color" + str(self.windowName), cv2.resize(color, (544, 408))
                )
                cv2.waitKey(1)
            elif mode == "ext":
                cv2.imshow(
                    "ExtCam" + str(self.windowName), cv2.resize(imdata, (640, 480))
                )
                cv2.waitKey(1)
            if mode == "tof":
                log.info("Printing imdata")
                print(imdata)
        except:
            log.warning("Bad frame")
        self.buffer = bytearray()
        self.frame_id += 1

    def readable(self):
        return True


class ExtStreamingClient(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.server_address = ("", port)
        # create a socket for TCP connection between the client and server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        log.debug("extStreamingClient created socket")
        self.socket.settimeout(5)

        self.bind(self.server_address)
        self.listen(10)

    def writable(self):
        return False  # don't want write notifies

    def readable(self):
        return True

    def handle_connect(self):
        print("connection recvied")

    def handle_accept(self):
        log.debug("extstreamingclient handle_accept")
        pair = self.accept()
        # print(self.recv(10))
        if pair is not None:
            sock, addr = pair
            log.info("Incoming external camera connection from %s" % repr(addr))
            # when a connection is attempted, delegate image receival to the ImageClient
            handler = ImageClient(sock, addr)


class RSStreamingClient(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.server_address = ("", port)
        # create a socket for TCP connection between the client and server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)

        self.bind(self.server_address)
        self.listen(10)

    def writable(self):
        return False  # don't want write notifies

    def readable(self):
        return True

    def handle_connect(self):
        print("connection recvied")

    def handle_accept(self):
        pair = self.accept()
        # print(self.recv(10))
        if pair is not None:
            sock, addr = pair
            log.info("Incoming rss connection from %s" % repr(addr))
            # when a connection is attempted, delegate image receival to the ImageClient
            handler = ImageClient(sock, addr)


class TOFStreamingClient(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.server_address = ("", port)
        # create a socket for TCP connection between the client and server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)

        self.bind(self.server_address)
        self.listen(10)

    def writable(self):
        return False  # don't want write notifies

    def readable(self):
        return True

    def handle_connect(self):
        log.info("connection recvied")

    def handle_accept(self):
        pair = self.accept()
        # print(self.recv(10))
        if pair is not None:
            sock, addr = pair
            log.info("Incoming tof connection from %s" % repr(addr))
            # when a connection is attempted, delegate image receival to the ImageClient
            handler = ImageClient(sock, addr)


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
        if mode == "rs":
            log.info("Preparing rss streaming client")
            client = RSStreamingClient()
        elif mode == "ext":
            log.info("Preparing external camera streaming client")
            client = ExtStreamingClient()
        elif mode == "tof":
            log.info("Preparing tof streaming client")
            client = TOFStreamingClient()
        log.debug("entering asyncore loop")
        asyncore.loop(30)

        # Look for responses from all recipients

    except socket.timeout:
        log.warning("timed out, no more responses")
    finally:
        log.info(sys.stderr, "closing socket")
        sock.close()


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)

    main(sys.argv[1:])
