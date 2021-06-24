#!/usr/bin/python
import sys, getopt
import asyncore
import numpy as np
import pickle
import socket
import struct
import cv2
import time

mc_ip_address = '224.0.0.1'
#mc_ip_address = '192.168.0.190'
#mode = "tof"
#mode = "rs"
mode = "rs"
ports = {"rs" : 1024,"tof" : 1025}
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
        if mode == "rs":
            cv2.namedWindow("depth"+str(self.windowName))
            cv2.namedWindow("color"+str(self.windowName))
        self.remainingBytes = 0
        self.frame_id = 0
       
    def handle_read(self):
        if self.remainingBytes == 0:
            # get the expected frame size
            recieved = self.recv(4)
            print(type(recieved))
            print(dir(recieved))
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
        # convert the frame from string to numerical data
        fps = 1/(time.time()-self.start_time)
        print(fps)
        self.start_time = time.time()
        imdata = pickle.loads(self.buffer)
        depth = imdata[:,0:320]
        color = np.clip(imdata[:,320:640],0, 256).astype('uint8')
        if mode == "rs":
            bigDepth = cv2.resize(depth, (0,0), fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
            bigDepth = np.clip(bigDepth, 0, 5000)
            bigDepth = cv2.applyColorMap((bigDepth/(5000/256)).astype(np.uint8), cv2.COLORMAP_RAINBOW) 
            cv2.imshow("depth"+str(self.windowName), cv2.resize(bigDepth, (544,408)))
            cv2.imshow("color"+str(self.windowName), cv2.resize(color, (544,408)))
            cv2.waitKey(1)
        if mode == "tof":
            print(imdata)
        self.buffer = bytearray()
        self.frame_id += 1
    def readable(self):
        return True

    
class StreamingClient(asyncore.dispatcher):
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
            print ('Incoming connection from %s' % repr(addr))
            # when a connection is attempted, delegate image receival to the ImageClient 
            handler = ImageClient(sock, addr)

def multi_cast_message(ip_address, port, message):
    # send the multicast message
    multicast_group = (ip_address, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connections = {}
    try:
        # Send data to the multicast group
        print('sending "%s"' % message + str(multicast_group))
        sent = sock.sendto(message.encode(), multicast_group)
        print('message sent')
        # defer waiting for a response using Asyncore
        client = StreamingClient()
        asyncore.loop()

        # Look for responses from all recipients
        
    except socket.timeout:
        print('timed out, no more responses')
    finally:
        print(sys.stderr, 'closing socket')
        sock.close()

if __name__ == '__main__':
    main(sys.argv[1:])
