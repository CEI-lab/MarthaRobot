import os
import sys
import time
import logging
import json
from pathlib import Path
from Configurations import *

sys.path.append(home + "HSI/HSI/commands/")
sys.path.append(home + "HSI/HSI/thread/")
sys.path.append(home + "HSI/HSI/commands/")
sys.path.append(home + "HSI/HSI/commands/text-to-speech-command")
sys.path.append(home + "HSI/HSI/commands/external-camera-command")
sys.path.append(home + "HSI/HSI/commands/internal-camera-command")
sys.path.append(home + "HSI/HSI/commands/process-project-image-command")
sys.path.append(home + "HSI/HSI/commands/get-images-names-command")
sys.path.append(home + "HSI/HSI/commands/set-speed-command")
sys.path.append(home + "HSI/HSI/commands/time-of-flight-command")
sys.path.append(home + "HSI/HSI/commands/read-IMU-command")
sys.path.append(home + "HSI/HSI/commands/bladder-command")
sys.path.append(home + "HSI/HSI/command-executer")
sys.path.append(home + "HSI/HSI/resources/registries/")
sys.path.append(home + "HSI/HSI/resources/queues/")
sys.path.append(home + "HSI/HSI/resources/classes")
sys.path.append(home + "HSI/HSI/tcp-manager")

sys.path.append(home + "/.local/lib/python3.7/site-packages/")

# Utility Classes
from ThreadManager import ThreadManager
from TCPManager import TCPManager
from CommandRegistry import CommandRegistry
from CommandExecuter import CommandExecuter

# Resource classes
from StatusQueue import StatusQueue
from CommandQueue import CommandQueue

# Command classes
from TextToSpeechCommand import TextToSpeechCommand
from ExternalCameraCommand import ExternalCameraCommand
from InternalCameraCommand import InternalCameraCommand
#from ProcessProjectImageCommand import ProcessProjectImageCommand
from GetImagesNamesCommand import GetImagesNamesCommand
from SetSpeedCommand import SetSpeedCommand
from TimeofFlightCommand import TimeofFlightCommand
from ReadIMUCommand import ReadIMUCommand
from BladderCommand import BladderCommand

#testExternalCameraSingle = True
#testExternalCameraContinuous = True

testInternalCameraSingle = True
#testInternalCameraContinuous = True

#testTOFSingle = True
#testTOFContinuous = True

# internal camera test
try:
    if testInternalCameraSingle:
        obj = InternalCameraCommand()
        obj.execute(None, {'type': 'single', 'priority': 1,'width':1280,'height':720})
except:
    pass
    
try:
    if testInternalCameraContinuous:
        obj = InternalCameraCommand()
        obj.execute(None, {'type': 'continuous-start', 'priority': 1})
except:
    pass

# tof test
try:
    if testTOFSingle:
        obj = TimeofFlightCommand()
        obj.execute(None, {'type': 'single', 'priority': 1})
except:
    pass
    
try:
    if testTOFContinuous:
        obj = TimeofFlightCommand()
        obj.execute(None, {'type': 'continuous-start', 'priority': 1})
except:
    pass

# external camera test
try:
    if testExternalCameraSingle:
        obj = ExternalCameraCommand()
        obj.execute(None, {'type': 'single', 'priority': 1})
except:
    pass
try:
    if testExternalCameraContinuous:
        obj = ExternalCameraCommand()
        obj.execute(None, {'type': 'continuous-start', 'priority': 1})
except:
    pass
