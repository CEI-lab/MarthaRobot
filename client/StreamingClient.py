#!/usr/bin/python
import sys, getopt
import asyncore
import numpy as np
import pickle
import socket
import struct
import cv2
import time
import logging

mc_ip_address = '10.50.26.63'
# mc_ip_address = '224.0.0.1'
#mc_ip_address = '192.168.0.190'
#mode = "tof"
mode = "rs"
# mode = "ext"
ports = {"rs" : 1024,"tof" : 1025, "ext": 1028}
port = ports[mode]
chunk_size = 4096

def main(argv):
    multi_cast_message(mc_ip_address, port, 'boop')
        
#UDP client for each camera server 
class ImageClient(asyncore.dispatcher):
    def __init__(self, server, source):   
        asyncore.dispatcher.__init__(self, server)
        self.start_time = time.time()
        self.address = server.getsockname()[0]
        self.port = source[1]
        self.buffer = bytearray()
        self.windowName = self.port
        # open cv window which is unique to the port 
        logging.info("Opening window")
        if mode == "rs":
            cv2.namedWindow("depth"+str(self.windowName))
            cv2.namedWindow("color"+str(self.windowName))
        elif mode == "ext":
            cv2.namedWindow("ExtCam"+str(self.windowName))
        self.remainingBytes = 0
        self.frame_id = 0
        logging.info("window setup complete")
       
    def handle_read(self):
        # logging.debug("imageclient handle_read")
        if self.remainingBytes == 0:
            # get the expected frame size
            recieved = self.recv(4)
            self.frame_length = struct.unpack('<I', recieved)[0]
            self.remainingBytes = self.frame_length
        
        # request the frame data until the frame is completely in buffer
        data = self.recv(self.remainingBytes)
        self.buffer += data
        self.remainingBytes -= len(data)
        # once the frame is fully recived, process/display it
        if len(self.buffer) == self.frame_length:
            self.handle_frame()

    def handle_frame(self):
        # logging.debug("imageclient handle_frame")

        # convert the frame from string to numerical data
        fps = 1/(time.time()-self.start_time)
        print(fps)
        self.start_time = time.time()
        try:
            imdata = pickle.loads(self.buffer)
            if mode == "rs":
                depth = imdata[:,0:320]
                color = np.clip(imdata[:,320:640],0, 256).astype('uint8')
                bigDepth = cv2.resize(depth, (0,0), fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
                bigDepth = np.clip(bigDepth, 0, 5000)
                bigDepth = cv2.applyColorMap((bigDepth/(5000/256)).astype(np.uint8), cv2.COLORMAP_RAINBOW)
                cv2.imshow("depth"+str(self.windowName), cv2.resize(bigDepth, (544,408)))
                cv2.imshow("color"+str(self.windowName), cv2.resize(color, (544,408)))
                cv2.waitKey(1)
            elif mode == "ext":
                cv2.imshow("ExtCam"+str(self.windowName), cv2.resize(imdata, (640,480)))
                cv2.waitKey(1)
            if mode == "tof":
                print(imdata)
        except:
            print("Bad frame")
        self.buffer = bytearray()
        self.frame_id += 1
    def readable(self):
        return True

    
class ExtStreamingClient(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.server_address = ('', port)
        # create a socket for TCP connection between the client and server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.debug("extStreamingClient created socket")
        self.socket.settimeout(5)
        
        self.bind(self.server_address) 	
        self.listen(10)

    def writable(self):
        return False # don't want write notifies

    def readable(self):
        return True
        
    def handle_connect(self):
        print("connection recvied")

    def handle_accept(self):
        logging.debug("extstreamingclient handle_accept")
        pair = self.accept()
        #print(self.recv(10))
        if pair is not None:
            sock, addr = pair
            logging.info('Incoming external camera connection from %s' % repr(addr))
            # when a connection is attempted, delegate image receival to the ImageClient 
            handler = ImageClient(sock, addr)

class RSStreamingClient(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.server_address = ('', port)
        # create a socket for TCP connection between the client and server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)

        self.bind(self.server_address)
        self.listen(10)

    def writable(self):
        return False # don't want write notifies

    def readable(self):
        return True

    def handle_connect(self):
        print("connection recvied")

    def handle_accept(self):
        pair = self.accept()
        #print(self.recv(10))
        if pair is not None:
            sock, addr = pair
            print('Incoming rss connection from %s' % repr(addr))
            # when a connection is attempted, delegate image receival to the ImageClient
            handler = ImageClient(sock, addr)

class TOFStreamingClient(asyncore.dispatcher):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.server_address = ('', port)
        # create a socket for TCP connection between the client and server
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)

        self.bind(self.server_address)
        self.listen(10)

    def writable(self):
        return False # don't want write notifies

    def readable(self):
        return True

    def handle_connect(self):
        print("connection recvied")

    def handle_accept(self):
        pair = self.accept()
        #print(self.recv(10))
        if pair is not None:
            sock, addr = pair
            print('Incoming tof connection from %s' % repr(addr))
            # when a connection is attempted, delegate image receival to the ImageClient
            handler = ImageClient(sock, addr)

def multi_cast_message(ip_address, port, message):
    # send the multicast message
    multicast_group = (ip_address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connections = {}
    try:
        # Send data to the multicast group
        logging.info('sending "%s"' % message + str(multicast_group))
        sent = sock.sendto(message.encode(), multicast_group)
        logging.debug('message sent')
        # defer waiting for a response using Asyncore
        if mode == "rs":
            logging.info("Preparing rss streaming client")
            client = RSStreamingClient()
        elif mode == "ext":
            logging.info("Preparing external camera streaming client")
            client = ExtStreamingClient()
        elif mode == "tof":
            logging.info("Preparing tof streaming client")
            client = TOFStreamingClient()
        logging.debug("entering asyncore loop")
        asyncore.loop(30)

        # Look for responses from all recipients
        
    except socket.timeout:
        print('timed out, no more responses')
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    main(sys.argv[1:])
