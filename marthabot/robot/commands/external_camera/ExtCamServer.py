#!/usr/bin/python
import pyrealsense2 as rs
import asyncore
import numpy as np
import pickle
import socket
import struct
import marthabot.configurations.robot_config as config
import time
import logging
import cv2

# mc_ip_address = '224.0.0.1'
mc_ip_address = '10.49.33.92'
# mc_ip_address = '192.168.0.176'
port = config.EXT_CAM_PORT
chunk_size = config.STREAM_CHUNK_SIZE


class ExtStreamingServer(asyncore.dispatcher):
    def __init__(self, address, jsonObject):
        asyncore.dispatcher.__init__(self)

        try:
            logging.info("Launching Ext Camera Server")
            if "width" in jsonObject and "height" in jsonObject:
                self.width = jsonObject["width"]
                self.height = jsonObject["height"]
            else:
                self.width = 480
                self.height = 640
        except:
            logging.error("Unexpected error: External Camera Streaming Server")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info('sending acknowledgement to {}'.format(address))

    # reduce the resolution of the depth image using post processing
        self.frame_data = ''
        self.connect((address[0], port))
        self.packet_id = 0

    def handle_connect(self):
        logging.info("connection received")

    def writable(self):
        return True

    def update_frame(self):
        self.camera = cv2.VideoCapture(config.USB_CAM_ID)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        ret, frame = self.camera.read()
        self.camera.release()
        if frame is not None:
            # convert the depth image to a string for broadcast
            frame = frame[:, :, ::-1]
            data = pickle.dumps(frame)
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


class ExtCamMulticastServer(asyncore.dispatcher):
    def __init__(self, jsonObject, host=mc_ip_address, port=port):
        self.jsonObject = jsonObject
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
            self.server = ExtStreamingServer(addr, self.jsonObject)
        except:
            logging.error("?RS")

    def writable(self):
        return False  # don't want write notifies

    def handle_close(self):
        self.close()

    def handle_accept(self):
        channel, addr = self.accept()

    def closeServer(self):
        asyncore.dispatcher.del_channel(self)
        self.server.close()
        self.close()
