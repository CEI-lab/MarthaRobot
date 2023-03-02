import json
import pickle
import os
import socket
import threading
import sys
from pathlib import Path
from multiprocessing import Lock
import time

from Configurations import *
from ComparableDict import ComparableDict

""" 
TCPManager that creates the tcp connection. 

CEI-LAB, Cornell University 2019
"""

class TCPManager(object):
    _instance = None
    _lock = Lock()

    def __new__(cls, command_queue, status_queue, command_event, status_event):
        """
        This method will make sure the TCPManager is singelton. 

            Inputs:
                None.

            Outputs:        
                None

        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, command_queue, status_queue, command_event, status_event):
        """
        This method will create the module TCPManager. 

            Inputs:
                None.

            Outputs:        
                None.
        """
        super().__init__()
        # establish the tcp socket 
        self._sock = None

        self._my_received_command_queue = command_queue
        self._my_status_queue = status_queue
        self._my_ip = CONFIGURATIONS.get("LOOP_BACK_IP_ADDRESS")
        self._my_raspi_ip = CONFIGURATIONS.get("RASPI_IP_ADDRESS")  # The address stays the same forever
        self._my_tcp_port = CONFIGURATIONS.get("TCP_PORT")
        self._my_last_ip = self._my_ip
        self._my_command_event = command_event
        self._my_status_event = status_event

    def __del__(self):
        """
        This method will delete the TCPManager class after it closes. 
            Inputs:
                None. 
            Outputs:        
                None
        """
        self._lock.acquire()
        if self._sock is not None:
            del (self._sock)

        self._lock.release()

    def _listenTCPHelper(self, connection, client_address):
        """
        """
        # while True:
            # Using the _test_json_object in TCPManagerTest.py, the json_object has "133" bytes after encode('utf-8')
            # data = connection.recv(CONFIGURATIONS.get("MAX_BYTES_OVER_TCP"))  # unit in bytes.
            # data = str(data.decode(CONFIGURATIONS.get("TCP_ENCODING")))
            # logging.info('TCPManager: TCP server received ' + data)

            # if data:
            #     jsonObject = self._parseJSONObject(data)
            #     jsonObject["clientIPAddress"] = client_address
            #     self._my_received_command_queue.enqueue(jsonObject)

        try:
            data = []
            while True:
                packet = connection.recv(4096)
                if not packet: break
                data.append(packet)
            if data != []:
                # TODO figure out why this was implemented incorrectly
                data_arr = ComparableDict(pickle.loads(b"".join(data)))
                #data_arr = ComparableDict(eval(data[0].decode()))
                data_arr["clientIPAddress"] = client_address
                self._my_received_command_queue.enqueue(data_arr)
                self._my_command_event.set()
        except Exception as ex:
            logging.error("_listenTCPHelper: " + str(ex))
        #finally:
        # try:
        #     connection.close()
        # except OSError:
        #     logging.error("TCPManager: The connection couldn't close in listenTCP. ")


    def listenTCP(self):
        """
        This method will be keep listening to the input data, parse it and enqueue to the command queue. 

            Inputs:
                None. 

            Outputs:        
                None

        """
        self._setServer()
        while True:
            try:
                logging.info('TCPManager: waiting for a connection')
                self._lock.acquire()
                connection, client_address = self._sock.accept()
                
                logging.info('TCPManager: client connected: ' + str(client_address))
                t1 = threading.Thread(target=self._listenTCPHelper, args=(connection, client_address[0],))
                t1.start()
            except Exception as ex:
                logging.info("TCPManager: Exception. " + str(ex))
            finally:
                self._lock.release()
                # try:
                #     connection.close()
                # except OSError:
                #     logging.error("TCPManager: The connection couldn't close in listenTCP. ")

    def _setServer(self):
        """
        This method will set the a server. 

            Inputs:
                None. 

            Outputs:
                None

        """
        self._lock.acquire()
        if self._sock is not None:
            del (self._sock)

        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            logging.info('TCPManager: starting up on port {}'.format(self._my_tcp_port))
            self._sock.bind(("", self._my_tcp_port))
            logging.info('TCPManager: after bind')
            self._sock.listen(CONFIGURATIONS.get("NUMBER_OF_ALLOWED_FAILED_TCP_CONNECTIONS"))
            logging.info('TCPManager: after listen')

        except:
            logging.error("TCPManager: set server can't create socket. ")

        finally:
            self._lock.release()

    # the parameter is backlog parameter. It specifies the number of unaccepted connectins
    # that the system will allow before refusing new connections. Starting in Python 3.5, it's optional.
    # If not specified, a default backlog value is chosen.

    def _parseJSONObject(self, received_json_string):
        """
        This method will parse the input string (eg. JSON object) into different key pairs. 

            Inputs:
                String that contain the command input from the sender. 

            Outputs:
                ValueObjects (eg. Command dictionaries) that is parsed from the string. 

        """
        try:
            # json.loads would parse the received json string into the json object
            _received_JSON_object = ComparableDict(json.loads(received_json_string))
            return _received_JSON_object

        except:
            logging.error("TCPManager: The json object in parseJSONObject is empty!")

    def _sendIPToRasPi(self):
        """
        Whenever there is a new IP address, this method will send it to the raspberry pi. 

            Inputs:
                None. 

            Outputs:
                None. 

        """
        
        try:
            logging.info("TCPManager: my ip changed from {} to {}".format(self._my_last_ip, self._my_ip))
            fname = CONFIGURATIONS.get("RASPI_TXT_FILE_FULL_PATH_NAME").format(home)
            os.remove(fname)
            with open(fname, 'a') as out_file:
                out_file.write("hsiip {}".format(self._my_ip) + "\n")

            os.system(CONFIGURATIONS.get("SENDING_IP_ADDRESS_TO_PI_COMMAND").format(fname, self._my_raspi_ip))

        except OSError:
            logging.error("TCPManager: Can't send IP to Rasberry Pi")

    def checkForNewIP(self):
        """
        This method will check if the host has changed the IP address or not. 

            Inputs:
                None. 

            Outputs:
                None. 

        """
        logging.info('TCPManager: check new IP')
        try:
            self._my_ip = os.popen('ip addr show wlan0').read().split("inet ")[1].split("/")[0]
        except:
            self._my_last_ip = self._my_ip
            logging.error('TCPManager: Please update myself IP address')
            self._my_ip = None

        ip_changed = True if self._my_last_ip != self._my_ip else False

        if ip_changed:
            self._sendIPToRasPi()

        self._my_last_ip = self._my_ip

    def sendOverTCP(self, valueObject):
        """
        This method will send the execute status to the sender side.  

            Inputs:
                ValueObject that indicate whether the execute status is successful or not. 

            Outputs:        
                None. 

        """
        
        try:
            logging.info("Start sending over tcp")
            
            logging.info("TCPManager: sending " + str(valueObject) + " to " + str(valueObject["clientIPAddress"]))
            
            client_address = valueObject["clientIPAddress"]

            port = valueObject.get("receivingPort")
            if port is None:
                port = CONFIGURATIONS.get("DEFAULT_RECEIVING_PORT")
            logging.info("TCPManager: Got the port {}".format(str(port)))
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            logging.info("TCPManager: Socket ready to send" + str(s))
            # connect to server on local computer
            s.connect((client_address,port))
            # message you send to server 
            message = pickle.dumps(valueObject)
            #message = str(valueObject).encode()
            # message sent to server 
            s.send(message)
            s.close()
            logging.info("TCPManager: sent data to the client {}. ".format(client_address))
            
        except Exception as ex:
            logging.error("TCPManager: coudn't send data to the client => " + str(ex))
        


    def checkForStatus(self):
        """
        This method will check if the status queue is empty or not and send status over. 

            Inputs:
                None. 

            Outputs:        
                None. 

        """
        while True:
            self._my_status_event.wait()
            if self._my_status_queue.size() > 0:
                status_obj = self._my_status_queue.dequeue()
                if status_obj is not None:
                    self.sendOverTCP(status_obj)
                else:
                    logging.warning("TCPManager: The statue queue has output a None object")
            else:
                self._my_status_event.clear()


if __name__ == "__main__":
    obj = TCPManager(None, None)
    print(obj.parseJSONObject(json.dumps({"cmd": "SetSpeed"})))
