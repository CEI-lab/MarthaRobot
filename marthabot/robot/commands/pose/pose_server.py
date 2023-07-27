#!/usr/bin/python
from asyncio import sleep
import asyncio
import pyrealsense2 as rs
import asyncore
import numpy as np
import pickle
import socket
import struct
# import marthabot.configurations.robot_config as config
import time
import logging
import cv2
import marthabot.configurations.robot_config as config

# port = config.REALSENSE_PORT
chunk_size = 4096



class PoseServer(asyncore.dispatcher):
    def __init__(self, address):
        asyncore.dispatcher.__init__(self)
        logging.info("Launching Realsense Camera Server")
        
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    
        self.pose_data = ''
        self.connect((config.CLIENT_IP, config.MAPPER_PORT))
        self.packet_id = 0

    def handle_connect(self):
        logging.info("connection received")

    def writable(self):
        return True

    def update_frame(self):
        message = "test"
        if message is not None:
            # convert the depth image to a string for broadcast
            data = pickle.dumps(message)
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
    def __init__(self):
        logging.info('MC Server init.')
        asyncore.dispatcher.__init__(self)
        server_address = ('', config.MAPPER_PORT)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(server_address)

    def handle_read(self):
        try:
            data, addr = self.socket.recvfrom(42)
            logging.info(
                'Recived Multicast message %s bytes from %s' % (data, addr))
           # Once the server recives the multicast signal, open the frame server
            self.server = PoseServer(addr)
        except:
            logging.error("?RS")

    def writable(self):
        return False  # don't want write notifies

    def handle_close(self):
        self.close()

    def handle_accept(self):
        channel, addr = self.accept()
        logging.info('received %s bytes from %s' % (channel, addr))

    def closeServer(self):
        print("Trying to close...")
        asyncore.dispatcher.del_channel(self)
        self.server.close()
        self.close()

async def main():
    server = RSMulticastServer()
    await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        print("Closing due to key combination")
        