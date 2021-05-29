import logging
import sys
import time
import serial
from multiprocessing import Lock
from pathlib import Path

from Configurations import *
import threading
from CommandInterface import CommandInterface

"""
Implementation of BladderCommand that will produce sound from text in json object.

CEI-LAB, Cornell University 2019
"""


class BladderCommand(CommandInterface):

    _t1 = None
    _lock = Lock()
    
    def __init__(self, port='/dev/ttyAMA0', baudrate=9600):
        """
        This method will initial the serial port for UART.
            Inputs:
                None.
            Outputs:        
                Return Instance. 
        
        """
        self._ser = serial.Serial(
            port=port,\
            baudrate=baudrate,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
            timeout=0)


    def __del__(self):
        self._ser.close()


    def _inflate_deflate(self, responseStatusCallback, jsonObject):
        """
        This method will be called to inflate and deflate the air channels.

        Inputs:
            responseStatusCallback : A callback function has to be passed, that will
                send status of command execution. This callback will be passed by the
                caller of execute().
            jsonObject : A JSON object containing text.

        Outputs:
            None
        """
        try:
            self._lock.acquire()
            jsonObject["response"] = "UNKNOWN_ERROR"
            send_binary_object = 0

            try:
                if self._ser.isOpen():
                    pair_numbers = CONFIGURATIONS.get("NUMBER_OF_AIRCHANNEL_PAIRS")
                    for index, select in enumerate(jsonObject["select"]):
                        send_binary_object = send_binary_object + select * (10**(pair_numbers - index - 1))
                    if jsonObject["action"] is "inflate":
                        send_binary_object = send_binary_object * 100 + 10
                        logging.info('BladderCommand : Inflate success')
                        jsonObject["response"] = "INFLATE_SUCCESS"
                    elif jsonObject["action"] is "deflate":
                        send_binary_object = send_binary_object * 100 + 1
                        logging.info('BladderCommand : Deflate success')
                        jsonObject["response"] = "DEFLATE_SUCCESS"
                    else:
                        send_binary_object = 0
                        logging.info('BladderCommand : There is a typo in the action field.')
                        jsonObject["response"] = "INCORRECT_INFLATE_DEFLATE_FIELD"
                    
                    self._ser.write((str(send_binary_object)+str('\n')).encode("ascii"))       
            except:
                logging.info('BladderCommand : can\'t open serial port.')
                jsonObject["response"] = "SERIAL_CONNECTION_CLOSED"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            logging.error('BladderCommand : Error probably in responseStatus call or resource is busy')
        finally:
            self._lock.release()


    def execute(self, responseStatusCallback, jsonObject):
        try:
            jsonObject["response"] = "ACTION_OR_SELECT_FIELD_NOT_IN_JSON"
            if "action" in jsonObject and "select" in jsonObject:

                if len(jsonObject["select"]) is CONFIGURATIONS.get("NUMBER_OF_AIRCHANNEL_PAIRS"):
                    self._t1 = threading.Thread(target=self._inflate_deflate, args=(responseStatusCallback, jsonObject,))
                    self._t1.start()
                    logging.info('BladderCommand : Process bladder command')
                    jsonObject["response"] = "PROCESS_BLADDER_COMMAND"
                else:
                    logging.info('BladderCommand : number of selection is incorrect.')
                    jsonObject["response"] = "ERROR_INCORRECT_SELECTION_NUMBER"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            logging.error('BladderCommand : Error no action or select field in json object')


if __name__ == "__main__":
    obj = BladderCommand()
    obj.execute(None, {"select" : [1,0,0],'action': "inflate"})
