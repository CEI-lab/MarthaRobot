#!/usr/bin/python
from asyncio import sleep
import asyncio
import sys
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
import asyncio_dgram as aiod


# port = config.REALSENSE_PORT
chunk_size = 4096
# log = logging.getLogger(__name__)
# log = None

sys.path.append("/home/pi/HSI/marthabot/utils")
from custom_logger import setup_logging

log = setup_logging(__name__)
log = logging.getLogger(__name__)


def get_pose(): 
    x,y,z = (0,0,0)
    t = 0.0
    c = 1.0
    ref = 0
    return [time.time(),x,y,z,t,c,ref]

active = asyncio.Event()
active.clear()

async def udp_reciever(port):
    stream = await aiod.bind((config.RASPI_IP_ADDRESS, port))
    log.info(f"Recieving on {stream.sockname}")
    
    while True:
        data, remote_addr = await stream.recv()
        data = data.decode()
        log.info(f"Recieved: {data} on port {port}")
        if data == "enable":
            log.info("enabling")
            active.set()
        elif data == "disable":
            log.info("disabling")
            active.clear()
        else:
            log.warning("Unknown command.")
        log.debug(f"active event: {active.is_set()}")
        await asyncio.sleep(0.01)

async def udp_dispatcher(port):
    stream = await aiod.connect((config.CLIENT_IP_ADDRESS, port))
    log.info(f"Sending to {stream.peername}")
    while True:
        
        log.info("Waiting for stream to be enabled")
        await active.wait()
        log.info("Sending pose data")
        while active.is_set():
            data = pickle.dumps(get_pose()) 
            await stream.send(data)

    await asyncio.sleep(0.5)
    log.info(f"Shutting down server")

class AsyncoreServerUDP(asyncore.dispatcher):
    def __init__(self, port, logger = logging.getLogger(__name__)):
        asyncore.dispatcher.__init__(self)
        self.log = logger
        # Bind to port 5005 on all interfaces
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(('', port))
        self.log.info(f"Bound server to {port}")

    # Even though UDP is connectionless this is called when it binds to a port
    def handle_connect(self):
        self.log.info(f"Server Started...") 

    # This is called everytime there is something to read
    def handle_read(self):
        self.log.debug("Handle read")
        data, addr = self.recv(2048)
        self.log.info(f"Recieved [{str(addr)}] from [{data}]")
        
    # This is called all the time and causes errors if you leave it out.
    def handle_write(self):
        pass

    def handle_accepted(self,sock,addr) -> None:
        self.log.debug(f"handle_accept with sock {sock} and addr {addr}")



class PoseServer(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        log.info("Launching Pose Server",{"overflow":
                                              f"Client IP: {config.CLIENT_IP_ADDRESS}\n"
                                              f"Port: {config.MAPPER_PORT}"}
                                            )
        
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)        
        self.pose_data = 'test'
        addr = ('',config.MAPPER_PORT)
        self.bind(addr)
        log.info("Binding PoseServer to {addr}")
        # self.connect((config.CLIENT_IP_ADDRESS, config.MAPPER_PORT))
        self.packet_id = 0
        self.streaming = False

    def handle_read(self):
        data, addr = self.recvfrom(config.BYTES_PER_PACKET)
        log.info(f"Recieved {data} from {addr}")

    def handle_connect(self):
        log.info("connection received")
        self.streaming = not self.streaming


    def writable(self):
        log.debug("confirm writable")
        return True

    def update_frame(self):
        log.debug("updating frame")
        message = "test"
        if message is not None:
            # convert the depth image to a string for broadcast
            data = pickle.dumps(message)
        # capture the lenght of the data portion of the message
            length = struct.pack('<I', len(data))
        # for the message for transmission
            self.frame_data = b''.join([length, data])

    def handle_write(self):
        log.debug("handle write")
        # first time the handle_write is called
        if not hasattr(self, 'frame_data'):
            log.debug("cerating new frame_data attr")
            self.update_frame()
    # the frame has been sent in it entirety so get the latest frame
        if len(self.frame_data) == 0:
            log.debug("updating frame since previous frame done")
            self.update_frame()
        else:
            log.debug("continuing to send previus frame")
            # send the remainder of the frame_data until there is no data remaining for transmition
            remaining_size = self.send(self.frame_data)
            self.frame_data = self.frame_data[remaining_size:]

    def handle_close(self):
        self.close()




if __name__ == "__main__":
    try:

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(udp_reciever(config.MAPPER_PORT), udp_dispatcher(config.MAPPER_PORT)))

    except:
        log.warning("Closing due to key combination")
        