"""
  A REPL implementation to send commands to and recieve responses from a marthabot 
  (ip specified in :data:`configurations.configurations.HOST`
"""
import pprint
import sys

sys.path.append("C:\\Users\\63nem\\Documents\\MarthaRobot\\")

import time
import socket
import pickle
import cv2
import numpy as np
import time
import traceback

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
    LOG.debug(data_arr)
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


# image = cv2.imread('137.png')


def parse_command(command: str) -> dict:
    """
    Parse and respond to text commands from the user.

    Commands

    -    motor [int left] [int right]
    -    hello
    -    sleep
    -    front [int speed]
    -    right [int speed]
    -    left [int speed]
    -    back [int speed]
    -    stop
    -    tts [string message]
    -    image ["list","get","upload","display"] [string filename ()]
    -    internal ["single", "continuous-start", "continuous-stop"]
    -    external ["single", "continuous-start", "continuous-stop"]
    -    bladder ["inflate","deflate",""] [int motor] [direction] [int distance]

    :param command: A human readable/input command
    :type command: str

    :return: A dictionary with the needed metadata to send to a marthabot
    :rtype: dict

    """
    if not command:
        return {}
    split = command.split()
    if not split:
        command = [command, ""]
    else:
        command = split
    if command[0] == "motor":
        return {
            "id": int(time.time()),
            "cmd": "SetSpeedCommand",
            "priority": 1,  # , Priority, type int
            "leftSpeed": -1 * int(command[1]),  # Left speed value, type int
            "rightSpeed": int(command[2]),  # Right speed value, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "hello":
        return {
            "id": int(time.time()),
            "cmd": "PrintHelloCommand",  # Command name
            "type": "hello",
            "height": 480,
            "width": 640,
            "count_period": 10,
            "colorize": 1,
            "priority": 1,  # , Priority, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "sleep":
        return {
            "id": int(time.time()),
            "cmd": "SleepTwentySecsCommand",  # Command name
            "type": "hello",
            "height": 480,
            "width": 640,
            "count_period": 10,
            "colorize": 1,
            "priority": 1,  # , Priority, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "front":
        return {
            "id": int(time.time()),
            "cmd": "SetSpeedCommand",
            "priority": 1,  # , Priority, type int
            "leftSpeed": -1 * int(command[1]),  # Left speed value, type int
            "rightSpeed": int(command[1]),  # Right speed value, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "back":
        return {
            "id": int(time.time()),
            "cmd": "SetSpeedCommand",
            "priority": 1,  # , Priority, type int
            "leftSpeed": int(command[1]),  # Left speed value, type int
            "rightSpeed": -1 * int(command[1]),  # Right speed value, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "left":
        return {
            "id": int(time.time()),
            "cmd": "SetSpeedCommand",
            "priority": 1,  # , Priority, type int
            "leftSpeed": int(command[1]),  # Left speed value, type int
            "rightSpeed": int(command[1]),  # Right speed value, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "right":
        return {
            "id": int(time.time()),
            "cmd": "SetSpeedCommand",
            "priority": 1,  # , Priority, type int
            "leftSpeed": -1 * int(command[1]),  # Left speed value, type int
            "rightSpeed": -1 * int(command[1]),  # Right speed value, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "stop":
        return {
            "id": int(time.time()),
            "cmd": "SetSpeedCommand",
            "priority": 1,  # , Priority, type int
            "leftSpeed": 0,  # Left speed value, type int
            "rightSpeed": 0,  # Right speed value, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "tts":
        return {
            "id": int(time.time()),
            "cmd": "TextToSpeechCommand",
            "text": " ".join(command[1:]),
            "priority": 1,  # , Priority, type int
        }
    elif command[0] == "image":
        if len(command) == 3:
            name = command[2]
        else:
            name = ""
        return {
            "id": int(time.time()),
            "cmd": "ImageCommand",  # Command name
            "type": command[1],  # list, get, upload, display
            "name": name,
            "priority": 1,  # , Priority, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "internal":
        return {
            "id": int(time.time()),
            "cmd": "InternalCameraCommand",  # Command name
            "type": command[1],  # single, continuous-start, continuous-stop
            "fps": 15,
            "priority": 1,  # , Priority, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "external":
        return {
            "id": int(time.time()),
            "cmd": "ExternalCameraCommand",  # Command name
            "type": command[1],  # single, continuous-start, continuous-stop
            "fps": 10,
            "priority": 1,  # , Priority, type int
            "receivingPort": config.RESPONSE_PORT,
            "height": 64,
            "width": 48,
        }
    elif command[0] == "rs":
        return {
            "id": int(time.time()),
            "cmd": "RealSenseCommand",  # Command name
            "type": command[1],  # single, continuous-start, continuous-stop
            "priority": 1,  # , Priority, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "tof":
        return {
            "id": int(time.time()),
            "cmd": "TimeofFlightCommand",  # Command name
            "type": command[1],  # single, stream
            "priority": 1,  # , Priority, type int
            "receivingPort": config.RESPONSE_PORT,
        }
    elif command[0] == "bladder":
        if len(command) == 5:
            return {
                "id": int(time.time()),
                "cmd": "BladderCommand",  # Command name
                "action": command[1],
                "motor": command[2],
                "direction": command[3],
                "dist": command[4],
                "priority": 1,  # , Priority, type int
                "receivingPort": 28200,
            }
        elif len(command) == 3:
            return {
                "id": int(time.time()),
                "cmd": "BladderCommand",  # Command name
                "action": command[1],  # single, stream
                "dist": command[2],
                "priority": 1,  # , Priority, type int
                "receivingPort": 28200,
            }
        else:
            return {
                "id": int(time.time()),
                "cmd": "UnknownCommand",  # Command name
                "action": command[1],  # single, stream
                "priority": 1,  # , Priority, type int
                "receivingPort": 28200,
            }
    elif command[0] in ["quit", "q"]:
        exit(0)
    else:
        print("Invalid command")
        return


# emergency stop
def exit_handler():
    """Function to handle unexpected failures.

    Should
    - Send a stop command to the robot to stop movement
    - Possibly stop bladder motors
    """
    sendObject(parse_command("stop"))


def main():
    # If the program crashses or otherwise closes try to sent a stop command
    atexit.register(exit_handler)

    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    LOG.info("Your Computer Name is:" + hostname)
    LOG.info("Your Computer IP Address is:" + IPAddr)
    LOG.info("Target Rover IP Address is:" + config.HOST)

    while True:
        print("\n")
        command = input("Enter command:\n")
        parsed = parse_command(command)
        LOG.info(f"Sending {parsed['cmd']} at {time.time()}")
        try:
            sendObject(parsed)
        except Exception as e:
            LOG.warning("Error while sending command")
            LOG.exception(e)
        receiveResponse(command, config.RESPONSE_PORT)


if __name__ == "__main__":
    main()
