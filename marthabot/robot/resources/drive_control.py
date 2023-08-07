import threading
from enum import Enum
import os
import time
from sympy import EX
import subprocess
import logging
import sys

sys.path.append("/home/pi/HSI/marthabot")

import marthabot.configurations.robot_config as config
log = logging.getLogger(__name__)


class MotorState(Enum):
    OFF = 0
    brakeING = 1
    EMERGENCY_BRAKE = 2
    MOVING = 3


class DriveControlLocked(Exception):
    pass


class DriveInvalidSpeed(Exception):
    pass


class DriveInvalidMotorAddress(Exception):
    pass


def validate_speeds(left, right):
    l2small = left < config.MIN_SPEED
    r2small = right < config.MIN_SPEED
    l2big = left > config.MAX_SPEED
    r2big = right > config.MAX_SPEED

    if l2small or r2small or l2big or r2big:
        message = ""
        if l2small:
            message += f"[Left speed of {left} is too small]"
        elif l2big:
            message += f"[Left speed of {left} is too big]"
        if r2small:
            message += f"[Right speed of {left} is too small]"
        elif r2big:
            message += f"[Right speed of {left} is too big]"

        raise DriveInvalidSpeed(message)

command = os.path.join(config.HOME_DIRECTORY,"robot","resources","SmcCmd","SmcCmd")

def check_config():
    info = subprocess.check_output([command, "-l"]).decode(sys.stdout.encoding)
    split = info.split("\n")
    addresses = []
    for line in split[1:-1]:
        addresses.append(line.split("#")[1])
    if config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID not in addresses or config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID not in addresses:
        addresses = "\n   ".join(addresses)
        message = ( f"Left: {config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID}\n"
                    f"Right: {config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID}\n"
                    f"Detected:\n   {addresses}"
                    )
        log.warning("Configuration does not match detected motor addresses",{"overflow":message})

def set_speed_script(left=None, right=None):
    command_string = ""
    if left is not None:
        command_string += f"{command} -d {config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID} --speed {left}  & "
    if right is not None:
        command_string += f"{command} -d {config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID} --speed {right} & "
    print(command_string)

    if command_string:
        subprocess.Popen(command_string,shell=True)
    else:
        log.warning("Tried to call set speed script but didn't set either motor.")


def brake_script(left=None, right=None):
    command_string = ""
    if left is not None:
        command_string += f"{command} -d {config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID} --brake {left} & "
    if right is not None:
        command_string += f"{command} -d {config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID} --brake {right} & "
    if command_string:
        subprocess.Popen(command_string,shell=True)
    else:
        log.warning("Tried to call brake script but didn't set either motor.")

def send_command(cmd):
    command_string = ""
    command_string += f"{command} -d {config.LEFT_WHEEL_SPEED_CONTROLLER_SERIAL_ID}  {cmd} & "
    command_string += f"{command} -d {config.RIGHT_WHEEL_SPEED_CONTROLLER_SERIAL_ID} {cmd} & "
    subprocess.Popen(command_string,shell=True)
   
def vel2motor(velocity):
    return int(velocity)
# TODO fix vel2motor

class SingletonDriveControl:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._l_state = MotorState.OFF
        self._r_state = MotorState.OFF
        self._l_speed = 0
        self._r_speed = 0

        self._e_lock = None
        self._lock = None

        self._update_event = threading.Event()

    def is_e_locked(self, key = None):
        return self._e_lock is not None or self._e_lock == key
    
    def is_locked(self, key = None):
        return self._lock is not None or self._lock == key
    
    def check_access(self, key = None):
        return not self.is_e_locked(key) and not self.is_locked(key)

    def set_speed(self, left, right, lock=None):
        if self._e_lock is not None:
            raise DriveControlLocked("Cannot set speed while emergency lock is set.")
        if self._lock is not None:
            if lock is not None and lock != self._lock:
                raise DriveControlLocked(
                    "Cannot set speed while another caller has locked the DriveController"
                )
            raise DriveControlLocked(
                "Must use key to set speed while DriveController is locked"
            )

        validate_speeds(left, right)

        self._l_speed = left
        self._r_speed = right
        # self.l_state = MotorState.MOVING if left != 0 else MotorState.OFF
        # self.r_state = MotorState.MOVING if right != 0 else MotorState.OFF

        set_speed_script(left,right)

        self._lock = lock

        self._update_event.set()
        self._update_event = threading.Event()

        return self._update_event
    


    def set_fwd_ang(self, fwd, ang, lock = None):
        diff = ang * config.WHEEL_BASE_LENGTH
        vr = fwd + diff / 2
        vl = fwd - diff / 2
        
        right = vel2motor(vr)
        left = vel2motor(vl)
        self.set_speed(left,right,lock)

    def emergency_brake(self, locker, enable, left = True, right = True, braking=True):
        if self.is_e_locked() and locker != self._e_lock:
            raise DriveControlLocked(
                "Cannot set emergency lock while emergency lock is already set."
            )

        brake_value = 32 if braking else 0
        if enable:
            self._e_lock = locker
            log.warning(f"Emergency brakes actiavated by {locker}")
            if left and right:
                brake_script(brake_value,brake_value)
            elif left:
                brake_script(left=brake_value)
            elif right:
                brake_script(right=brake_value)
            else:
                log.warning("Called emergency break, but did not break left or right motors.")
        else:
            log.info(f"Emergency brakes deactivated by {locker}")
            self._e_lock = None
        
        self._update_event.set()
        self._update_event = threading.Event()

        return self._update_event

    @property
    def l_speed(self):
        return self._l_speed

    @property
    def r_speed(self):
        return self._r_speed
    
    @property
    def speed(self):
        return (self.l_speed,self.r_speed)

    @property
    def l_state(self):
        return self._l_state

    @property
    def r_state(self):
        return self._r_state




check_config()
send_command("--resume")
# set_speed_script(1000,1000)

dc = SingletonDriveControl()
# dc.set_speed(200,200)
dc.set_fwd_ang(1000,3)
time.sleep(1)

# for i in range(32):
#     print(i+1)
#     set_speed_script((i+1)*100,(i+1)*100)
#     time.sleep(10)
#     brake_script(32,32)
#     time.sleep(3)

brake_script(32,32)
send_command("--stop")
