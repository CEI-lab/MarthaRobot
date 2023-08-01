"""
  A REPL implementation to send commands to and recieve responses from a marthabot 
  (ip specified in :data:`configurations.configurations.HOST`
"""

import sys
import os
from pynput import keyboard
from pynput.keyboard import Key


# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)

import time
import socket
import pickle
import cv2
import numpy as np
import time
import traceback
import pprint


# import logging
from marthabot.utils.custom_logger import setup_logging
from utils.printers import pp

LOG = setup_logging(__name__)


import marthabot.configurations.robot_config as config


import atexit


def sendObject(message: dict):
    """
    sendObject Send a command dictionary to the robot

    :param message: Dictionary defining a command
    :type message: dict
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to robot
    s.connect((config.HOST, config.COMMAND_PORT))

    # send pickled command
    s.send(pickle.dumps(message))
    s.close()


def sendAgainAndAgain():
    """Helper function to repeatedly send a command"""
    while True:
        myCommand = "ext single"
        sendObject(parse_command(myCommand))
        print("\n")
        print(time.time())
        receiveResponse(myCommand, 28200)


def receiveResponse(command: str, port: int):
    """Wait for and handle response from the robot.

    :param command: Raw command that was input
    :type command: str
    :param port: Port to listen for a response on
    :type port: int
    """
    command = command.split()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(1)

    s.bind(("", port))
    s.listen(5)
    connection, address = s.accept()
    data = []
    # collect all packets
    while True:
        packet = connection.recv(config.BYTES_PER_PACKET)
        if not packet:
            break
        data.append(packet)
    s.close()
    data_arr = pickle.loads(b"".join(data))
    # LOG.debug(data_arr)
    if (
        command[0] == "image"
        and command[1] == "get"
        or command[0] == "int"
        and command[1] == "single"
        or command[0] == "ext"
        and command[1] == "single"
        or command[0] == "rs"
        and command[1] == "single"
    ):
        try:
            if command[0] == "int" or command[0] == "ext":
                cv2.imshow("image", data_arr["data"][:, :, ::-1])
            if command[0] == "image" or command[0] == "rs":
                cv2.imshow("image", data_arr["data"] / np.amax(data_arr["data"]))
            cv2.waitKey(1)
        except Exception as e:
            LOG.warning("Problem recieving/displaying image response")
            LOG.warning(f"Raw response: \n{pp.pformat(data_arr)}")
            LOG.exception(e)
            pass
    #    elif command[0] == "ext" and command[1] == "streaming":
    #        sendAgainAndAgain()
    else:
        try:
            if "data" in data_arr:
                LOG.info("response was: \n")
                LOG.info(data_arr["data"])
            elif command[0] in ["hello"]:
                LOG.info(f"Recieved {pp.pformat(data_arr)}")
            else:
                LOG.warning("No 'data' field in response.")
                LOG.warning(f"Raw response: \n{pp.pformat(data_arr)}")
        except Exception as e:
            LOG.warning("Problem receiving response")
            LOG.exception(e)
            pass


# emergency stop
def exit_handler():
    """Function to handle unexpected failures.

    Should
    - Send a stop command to the robot to stop movement
    - Possibly stop bladder motors
    """
    LOG.info("Exiting, sending stop command")
    command = parse_command("stop")
    sendObject(command)
    # receiveResponse("stop", config.RESPONSE_PORT)


keys = []
left = 0
right = 0
speed = 1000


def on_key_release(key):
    global left
    global right
    global keys
    if key not in keys:
        return

    if key == Key.right and Key.right in keys:
        keys.remove(Key.right)
        left -= speed
        right += speed
    elif key == Key.left and Key.left in keys:
        keys.remove(Key.left)
        left += speed
        right -= speed
    elif key == Key.up and Key.up in keys:
        keys.remove(Key.up)
        left -= speed
        right -= speed
    elif key == Key.down and Key.down in keys:
        keys.remove(Key.down)
        left += speed
        right += speed
    elif key == Key.esc:
        exit()
    if len(keys) == 0:
        left = right = 0
    print("Motors: ", left, right)
    parsed = parse_command(f"motor {left} {right}")
    if "cmd" in parsed:
        LOG.info(f"Sending {parsed['cmd']} at {time.time()}")
        try:
            sendObject(parsed)
        except Exception as e:
            LOG.warning("Error while sending command")
            LOG.exception(e)
    else:
        LOG.warning("Invalid command")


def on_key_press(key):
    global left
    global right
    global keys
    if key in keys:
        return
    if key == Key.right:
        keys.append(Key.right)
        left += speed
        right -= speed
    elif key == Key.left:
        keys.append(Key.left)
        left -= speed
        right += speed
    elif key == Key.up:
        keys.append(Key.up)
        left += speed
        right += speed
    elif key == Key.down:
        keys.append(Key.down)
        left -= speed
        right -= speed
    elif key == Key.esc:
        exit()
    print("Motors: ", left, right)
    parsed = parse_command(f"motor {left} {right}")
    if "cmd" in parsed:
        LOG.info(f"Sending {parsed['cmd']} at {time.time()}")
        try:
            sendObject(parsed)
        except Exception as e:
            LOG.warning("Error while sending command")
            LOG.exception(e)
    else:
        LOG.warning("Invalid command")


if __name__ == "__main__":
    with keyboard.Listener(
        on_press=on_key_press, on_release=on_key_release
    ) as listener:
        listener.join()

# if __name__ == "__main__":
#     # If the program crashses or otherwise closes try to sent a stop command
#     atexit.register(exit_handler)

#     hostname = socket.gethostname()
#     IPAddr = socket.gethostbyname(hostname)
#     LOG.info("Your Computer Name is:" + hostname)
#     LOG.info("Your Computer IP Address is:" + IPAddr)
#     LOG.info("Target Rover IP Address is:" + config.HOST)

#     while True:
#         print("\n")
#         command = input("Enter command:\n")
#         parsed = parse_command(command)
#         print(parsed)
#         if "cmd" in parsed:
#             LOG.info(f"Sending {parsed['cmd']} at {time.time()}")
#             try:
#                 sendObject(parsed)
#             except Exception as e:
#                 LOG.warning("Error while sending command")
#                 LOG.exception(e)
#             receiveResponse(command, config.RESPONSE_PORT)
#         else:
#             LOG.warning("Invalid command")
