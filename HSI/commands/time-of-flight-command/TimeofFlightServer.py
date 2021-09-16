#!/usr/bin/python   
import asyncore
import numpy as np
import pickle
import socket
import struct
from Configurations import *
import time
import RPi.GPIO as GPIO
import VL53L0X
import logging

mc_ip_address = '224.0.0.1'
port = CONFIGURATIONS["TOF_PORT"]
chunk_size = 4096

class DevNullHandler(asyncore.dispatcher_with_send):

    def handle_read(self):
        logging.info(self.recv(1024))

    def handle_close(self):
        self.close()
           
class StreamingServer(asyncore.dispatcher):
    def __init__(self, address):
        asyncore.dispatcher.__init__(self)
        try:
            self.shutdown_pins = CONFIGURATIONS["TOF_PINS"]
            GPIO.setmode(GPIO.BCM)
          
            for pin in self.shutdown_pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
            time.sleep(0.5)
            self.tof_objects = {}
            self.tof_objects[self.shutdown_pins[0]] = VL53L0X.VL53L0X(address=0x2A)
            self.tof_objects[self.shutdown_pins[1]] = VL53L0X.VL53L0X(address=0x2C)
            self.tof_objects[self.shutdown_pins[2]] = VL53L0X.VL53L0X(address=0x2E)
            for pin in self.shutdown_pins:
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(0.50)
                self.tof_objects[pin].start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
        except:
            logging.error("Unexpected error: ToF Streaming Server")
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.frame_data = ''
        self.connect((address[0], port))
        self.packet_id = 0        

    def handle_connect(self):
        logging.info("ToF streaming server connection received")

    def writable(self):
        return True

    def update_frame(self):
        time.sleep(CONFIGURATIONS["TIMEOFFLIGHT_COUNT_PERIOD"])
        distances = [0,0,0]

        GPIO.setmode(GPIO.BCM)
        for i in range(3):
            distance = self.tof_objects[self.shutdown_pins[i]].get_distance()
            while (distance == -1):
                GPIO.output(self.shutdown_pins[i], GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(self.shutdown_pins[i], GPIO.HIGH)
                time.sleep(0.1)
                self.tof_objects[self.shutdown_pins[i]].start_ranging(VL53L0X.VL53L0X_BETTER_ACCURACY_MODE)
            distances[i] = distance
            
        # convert the depth image to a string for broadcast
        data = pickle.dumps(distances)
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
        try:
            GPIO.setmode(GPIO.BCM)
            for pin in self.shutdown_pins:
                self.tof_objects[pin].stop_ranging()
            GPIO.cleanup()
        except:
            pass
        time.sleep(1)
        self.close()
            

class TOFMulticastServer(asyncore.dispatcher):
    def __init__(self, host = mc_ip_address, port=port):
        asyncore.dispatcher.__init__(self)
        server_address = (host, port)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(server_address)   

    def handle_read(self):
        try:
            data, addr = self.socket.recvfrom(42)
            logging.info('Recived Multicast message %s bytes from %s' % (data, addr))
           # Once the server recives the multicast signal, open the frame server
            self.server = StreamingServer(addr)
        except:
            logging.error("?TOF")

    def writable(self): 
        return False # don't want write notifies

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


