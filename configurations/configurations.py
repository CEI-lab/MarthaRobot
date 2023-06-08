"""
(b)Constants and variables for use throughout the project.  Includes GPIO pin numbers, IP addresses, hardware addresses, and more. 
"""

import logging
import os


import tokenize
from io import StringIO
from collections import namedtuple
import black


home = os.path.expanduser("~pi")

# Projector
# IMPORTANT : Image folder will always be in home directory with name 'Images'
IMAGES_DIRECTORY = "{}/Images/"
""" Directory projector images will be stored in on the RPi """
SHOW_DEFAULT_IMAGE = True
""" 
Whether to display an image on startup of the robot
Not currently in use - TODO remove or implement
"""
DEFAULT_IMAGE_ON_STARTUP = "__0__.jpg"
""" File address of the image that should be shown on startup """

DISPLAY_IMAGE = None
""" Variable to store the name of the current image being displayed """


# TCP
TCP_PORT = 65432
""" Port to send TCP messages from computer -> rover """
TCP_ENCODING = "utf-8"
""" Encoding used for TCP """
DEFAULT_RECEIVING_PORT = 28200
""" Port to send TCP messages from rover -> computer """
NUMBER_OF_ALLOWED_FAILED_TCP_CONNECTIONS = 1000
""" Number of failed TCP connections before :func:`robot.tcp_manager.TCPManager._setServer` will fail """
MAX_BYTES_OVER_TCP = 1024
""" TCP packet size """

# Misc connection
RASPI_IP_ADDRESS = "199.168.1.212"
""" The IP address of the rover's RPi """
LOOP_BACK_IP_ADDRESS = "127.0.0.1"
""" Loopback address for the RPi """
CHECK_NEW_IP_FROM_PI_FREQUENCY = 0.333
""" Frequency to check whether the rover's IP address has changed """
RASPI_TXT_FILE_FULL_PATH_NAME = "{}/HSI/ip.txt"
"""
The file address on the 'server' RPi to store the IP address in
Implemented, but not actively used since IPs in our setup remain constant for the most part
"""
SENDING_IP_ADDRESS_TO_PI_COMMAND = (
    "sudo -u pi scp -rp {} pi@{}:/home/pi/MEng/meng-hsi-group/tcp"
)
"""
String representation of the command used to scp the IP file
Might not currently be configured correctly, consider referencing :data:`RASPI_TXT_FILE_FULL_PATH_NAME`
"""


# Drive motors
SPEED_CONTROLLER_COMMAND = "{}/HSI/HSI/resources/SmcCmd/./SmcCmd"
"""
File address to the command for interacting with the motor controller.
These motor controllers do not have a python library so they are controlled by calling an external script.
"""
LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID = "33FF-6D06-4D4B-3731-1919-1543"
""" Serial ID to send commands to the left motor controller """
RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID = "52FF-7606-7283-5255-1917-2267"
""" Serial ID to send commands to the right motor controller """

# Logging
ENABLE_FILE_LOGGING = False
LOG_FILENAME = "{}/hsi.log"  # Always in home directory
LOGGING_LEVEL = logging.DEBUG  # For detailed logs change this to 'logging.DEBUG'

# Time of flight sensors
TOF_PINS = [13, 26, 27]  # BCM [left middle right] (Possibly disable/enable pins)
TOF_ADDR = [0x2A, 0x2C, 0x2E]
# Keep reading=time-of-flight measurements and only send periodically on reading count.
TIMEOFFLIGHT_COUNT_PERIOD = 0.5

# Streaming Ports
REALSENSE_PORT = 1024
TOF_PORT = 1025
EXT_CAM_PORT = 1028
DEFAULT_EXCAM_PORT = 1026
DEFAULT_INCAM_PORT = 1027

# Cameras
USB_CAM_ID = "/dev/v4l/by-id/usb-HD_Camera_Manufacturer_VGA_USB_Camera_VGA_USB_Camera-video-index0"
RTSP_COMMAND = "resources/v4l2rtspserver/v4l2rtspserver"

# bladder motor 1
DIR1_1_PIN = 10
DIR2_1_PIN = 18
M1_ADDRESS = 0x5E
M1_SELECT = 1
ENC1_1_PIN = 9
ENC2_1_PIN = 25

# bladder motor 2
DIR1_2_PIN = 24
DIR2_2_PIN = 15
M2_ADDRESS = 0x5E
M1_SELECT = 0
ENC1_2_PIN = 17
ENC2_2_PIN = 18

# bladder motor 3
DIR1_3_PIN = 0
DIR2_3_PIN = 22
M3_ADDRESS = 0xDE
M1_SELECT = 0
ENC1_3_PIN = 19
ENC2_3_PIN = 6

# bladder fan
FAN_PIN = 21
""" PWM pin to power the bladder fan."""
BLADDER_SIZE = [160, 160, 160]
""" Size of the bladder.  Should be a 3 int list representing the distance
    each bladder motor can travel before the bladder reaches full inflation.
    Asymetric bladders may have different values for each motor.
"""
BLADDER_SPEED = 250
""" A default speed for the bladder motors. """


# client.py
# TODO combine TCP_PORT with COMMAND_PORT
HOST = "192.168.0.191"
"""IP of the MarthaBot to connect to."""

COMMANDPORT = 65432
""" Port to send commands from computer -> rover

    Should match :data:`~configurations.configurations.TCP_PORT`
"""
BYTES_PER_PACKET = 4096
""" 
Bytes per command packet.
Might currently be incorrectly configured to be different from :data:`~configurations.configurations.MAX_BYTES_OVER_TCP`
"""
RESPONSE_PORT = 28200
""" 
Port to send commands from rover -> computer
Should match :data:`~configurations.configurations.DEFAULT_RECIEVING_PORT`
"""


# streaming_client.py
STREAM_PORTS = {"rs": 1024, "tof": 1025, "ext": 1028}
MC_IP_ADDRESS = "224.0.0.1"
STREAM_CHUNK_SIZE = 4096

# RPI server to get IPs
RPI_SERVER = 10


# UNUSED
# These seem to be unused TODO check that removing them is safe
NUMBER_OF_AIRCHANNEL_PAIRS = 3  # Number of air-channel pairs or systems.
DEFAULT_IMAGE_DEFAULT_LOCATION = "{}/HSI/resources/defaults/"
DEFAULT_IMAGE_OTHER_LOCATION = "{}/Images/"


def update(k: str, v: str):
    """Modify the :mod:`configurations.configurations` source file to update the value assigned to a variable.

    Implemented with two possible use cases in mind
        - Modifying the client side file to match the currently connected robot's file
        - Guided command line setup of a newly built robot

    :param k: The name of the variable to be modified
    :type k: str
    :param v: The new value to be written
    :type v: str
    """
    collected = []
    with open(__file__, "r") as f:
        g = tokenize.generate_tokens(f.readline)
        notfound = True
        for token in g:
            # print(token)
            type, string, _, _, _ = token
            collected.append((type, string))
            if type == tokenize.NAME and string == k:
                op = next(g)
                optype, opstring, _, _, _ = op
                val = next(g)
                valtype, value, _, _, _ = val

                if notfound and optype == tokenize.OP and opstring == "=":
                    logging.info(f"Configuration {string} updated from {value} to {v}")
                    collected.append((tokenize.OP, "="))
                    notfound = False
                    if valtype == tokenize.NUMBER:
                        if str.isnumeric(v):
                            collected.append((tokenize.NUMBER, str(v)))
                        else:
                            collected.append(value)
                    elif valtype == tokenize.STRING:
                        collected.append((tokenize.STRING, str(v)))

                else:
                    collected.append((optype, opstring))
                    collected.append((valtype, value))

    newSource = tokenize.untokenize(collected)
    formated = black.format_str(newSource, mode=black.Mode())
    with open(__file__, "w") as f:
        f.write(formated)
