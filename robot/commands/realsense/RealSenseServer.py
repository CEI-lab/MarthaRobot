#!/usr/bin/python
import pyrealsense2 as rs
import asyncore
import numpy as np
import pickle
import socket
import struct
from configurations.Configurations import *
import time
import logging
import cv2

# mc_ip_address = '224.0.0.1'
mc_ip_address = '10.49.33.92'
# mc_ip_address = '192.168.0.176'
port = CONFIGURATIONS["REALSENSE_PORT"]
chunk_size = 4096


def getDepthAndTimestamp(pipeline, depth_filter):
    frames = pipeline.wait_for_frames()
    # take owner ship of the frame for further processing
    frames.keep()
    depth = frames.get_depth_frame()
    rgb = frames.get_color_frame()
    if depth:
        depth2 = depth_filter.process(depth)
        # take owner ship of the frame for further processing
        depth2.keep()
        # represent the frame as a numpy array
        depthData = depth2.as_frame().get_data()
        depthMat = np.asanyarray(depthData)
        color_image = cv2.resize(cv2.cvtColor(np.asanyarray(
            rgb.get_data()), cv2.COLOR_BGR2GRAY), (320, 240))
        ts = frames.get_timestamp()
        return np.hstack((depthMat, color_image)), ts
    else:
        return None, None


def openPipeline():
    cfg = rs.config()
    cfg.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    cfg.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipeline = rs.pipeline()
    pipeline_profile = pipeline.start(cfg)
    sensor = pipeline_profile.get_device().first_depth_sensor()
    return pipeline


class DevNullHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        logging.info(self.recv(1024))

    def handle_close(self):
        self.close()


class RSStreamingServer(asyncore.dispatcher):
    def __init__(self, address):
        asyncore.dispatcher.__init__(self)
        logging.info("Launching Realsense Camera Server")
        try:
            self.pipeline = openPipeline()
        except:
            logging.error("Unexpected error: Real Sense Streaming Server")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info('sending acknowledgement to {}'.format(address))

    # reduce the resolution of the depth image using post processing
        self.decimate_filter = rs.decimation_filter()
        self.decimate_filter.set_option(rs.option.filter_magnitude, 2)
        self.frame_data = ''
        self.connect((address[0], port))
        self.packet_id = 0

    def handle_connect(self):
        logging.info("connection received")

    def writable(self):
        return True

    def update_frame(self):
        depth, timestamp = getDepthAndTimestamp(
            self.pipeline, self.decimate_filter)
        if depth is not None:
            # convert the depth image to a string for broadcast
            data = pickle.dumps(depth)
        # capture the lenght of the data portion of the message
            length = struct.pack('<I', len(data))
        # for the message for transmission
            self.frame_data = b''.join([length, data])

    def handle_write(self):
        # first time the handle_write is called
        if not hasattr(self, 'frame_data'):
            self.update_frame()
    # the frame has been sent in it entirety so get the latest frame
        if len(self.frame_data) == 0:
            self.update_frame()
        else:
            # send the remainder of the frame_data until there is no data remaining for transmition
            remaining_size = self.send(self.frame_data)
            self.frame_data = self.frame_data[remaining_size:]

    def handle_close(self):
        self.close()


class RSMulticastServer(asyncore.dispatcher):
    def __init__(self, host=mc_ip_address, port=port):
        logging.info('MC Server init.')
        asyncore.dispatcher.__init__(self)
        server_address = ('', port)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(server_address)

    def handle_read(self):
        try:
            data, addr = self.socket.recvfrom(42)
            logging.info(
                'Recived Multicast message %s bytes from %s' % (data, addr))
           # Once the server recives the multicast signal, open the frame server
            self.server = RSStreamingServer(addr)
        except:
            logging.error("?RS")

    def writable(self):
        return False  # don't want write notifies

    def handle_close(self):
        self.close()

    def handle_accept(self):
        channel, addr = self.accept()
        logging.info('received %s bytes from %s' % (data, addr))

    def closeServer(self):
        print("Trying to close...")
        asyncore.dispatcher.del_channel(self)
        self.server.close()
        self.close()
