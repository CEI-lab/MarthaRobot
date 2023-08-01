"""
Command module for controlling the inflatable bladder.

CEI-LAB, Cornell University 2023
"""

from __future__ import print_function
import asyncio
import time
from multiprocessing import Lock
import logging
import qwiic_scmd
from enum import Enum

log = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except:
    log.warning("Could not import RPi.GPIO, importing MOCK module instead")
    from marthabot.robot.mock import MOCK_rpigpio as GPIO


import marthabot.configurations.robot_config as config
import threading
from commands.command_interface import CommandInterface



class BladderCommand(CommandInterface):
    _t1 = None
    # _lock = Lock()

    def __init__(self):
        """
        Create a Bladder Command object.  Takes in commands and performs the appropriate actions.
        """
        GPIO.setmode(GPIO.BCM)

        # self._m1Event: ChildEvent = ChildEvent()
        # self._m2Event: ChildEvent = ChildEvent()
        # self._m3Event: ChildEvent = ChildEvent()

        # self._all_motor_event = AndEvent(self._m1Event,
        #                                 self._m2Event,
        #                                 self._m3Event,)


        self._m1Event = threading.Event()
        self._m2Event = threading.Event()
        self._m3Event = threading.Event()


        self.m1 = BladderMotor(
            config.M1_ADDRESS,
            config.M1_SELECT,
            self._m1Event,
            config.ENC1_1_PIN,
            config.ENC2_1_PIN,
        )
        self.m2 = BladderMotor(
            config.M2_ADDRESS,
            config.M2_SELECT,
            self._m2Event,
            config.ENC1_2_PIN,
            config.ENC2_2_PIN,
        )
        self.m3 = BladderMotor(
            config.M3_ADDRESS,
            config.M3_SELECT,
            self._m3Event,
            config.ENC1_3_PIN,
            config.ENC2_3_PIN,
        )

        # log.debug(self.m1,self.m2,self.m3)
        # Setup and start PWM on the fan pin, with 0 duty cycle
        GPIO.setup(config.FAN_PIN, GPIO.OUT)
        self.fan: GPIO.PWM = GPIO.PWM(config.FAN_PIN, 1000)
        self.fan.start(0)

    def __del__(self):
        """
        Override built in to disable/stop motors before deleting this object.
        """
        self.m1.motor.disable()
        self.m2.motor.disable()
        self.m3.motor.disable()
        self.fan.stop()

    def stop(self):
        """
        Stop all of the bladder motors.  Leaves fan running to keep bladder inflated.
        """
        self.m1.stop()
        self.m2.stop()
        self.m3.stop()

    def move_all(self, direction, speed):
        """
        move_all Move all bladder motors at a specified speed.

        Valid options for direction are ["out",1,"in",0]

        :param direction: Direction to move motors
        :type direction: str, int
        :param speed: Speed to move at.
        :type speed: int
        """
        self.m1.move(direction, speed)
        self.m2.move(direction, speed)
        self.m3.move(direction, speed)

        

    async def move_all_dist(self, dist1, dist2, dist3, direction, speed):
        """
        Move all bladder motors a distance in a specified direction, using :func:`.bladder.bladder_motor.bladder_motor.move_distance`

        Valid options for direction are ["out",1,"in",0]

        :param direction: Direction to move motors
        :type direction: str, int
        :param dist1: Distance to move motor 1
        :type dist1: int
        :param dist2: Distance to move motor 2
        :type dist2: int
        :param dist2: Distance to move motor 3
        :type dist3: int
        """
        # TODO distinct speed per motor, or scale all based on longest dist
        log.debug("Moving bladder motors")
        self.m1.move_distance(direction, speed, dist1)
        self.m2.move_distance(direction, speed, dist2)
        self.m3.move_distance(direction, speed, dist3)

        async with asyncio.TaskGroup() as tg:
            tg: asyncio.TaskGroup = tg
            tg.create_task(await self.m1.wait())
            tg.create_task(await self.m2.wait())
            tg.create_task(await self.m3.wait())
        log.debug("Finished moving bladder motors")




    

    def inflate(self):
        """
        Inflate the robot's bladder completely.  Delays after turning on the fan
        to allow the bladder to inflate before starting to release the pulleys.
        """
        # TODO make sure the encoder based endswitch code is carried over to this file
        self.fan.ChangeDutyCycle(100)
        time.sleep(10)
        self._m1Event.clear()
        self._m2Event.clear()
        self._m3Event.clear()
        self.move_all_dist(
            config.BLADDER_SIZE[0],
            config.BLADDER_SIZE[1],
            config.BLADDER_SIZE[2],
            "out",
            config.BLADDER_SPEED,
        )
        self._m1Event.wait()
        self._m2Event.wait()
        self._m3Event.wait()

    def deflate(self):
        """
        Deflate the robots bladder completely
        """
        self.fan.ChangeDutyCycle(100)
        self._m1Event.clear()
        self._m2Event.clear()
        self._m3Event.clear()
        self.move_all_dist(
            config.BLADDER_SIZE[0],
            config.BLADDER_SIZE[1],
            config.BLADDER_SIZE[2],
            "in",
            config.BLADDER_SPEED,
        )
        self._m1Event.wait()
        self._m2Event.wait()
        self._m3Event.wait()
        self.fan.ChangeDutyCycle(0)

    def _inflate_deflate(self, responseStatusCallback, jsonObject):
        """
        This method will be called to inflate and deflate the air bladder.

        :param responseStatusCallback:  A callback function that will send status of command execution. This callback will be passed by the caller of :meth:`execute`.

        :param jsonObject: Command to execute, which will also be used to pass back information as a response.  A dictionary created from a json object.
        :type jsonObject: dict

        """
        try:
            jsonObject["response"] = "UNKNOWN_ERROR"
            try:
                if jsonObject["action"] == "inflate":
                    log.info("Inflating...")
                    self.inflate()
                    log.info("BladderCommand : Inflate success")
                    jsonObject["response"] = "INFLATE_SUCCESS"
                elif jsonObject["action"] == "deflate":
                    log.info("Deflating...")
                    self.deflate()
                    log.info("BladderCommand : Deflate success")
                    jsonObject["response"] = "DEFLATE_SUCCESS"
                else:
                    log.info("Error...")
                    log.info(
                        "BladderCommand : There is a typo in the action field."
                    )
                    jsonObject["response"] = "INCORRECT_INFLATE_DEFLATE_FIELD"

            except:
                log.info("BladderCommand : can't open serial port.")
                jsonObject["response"] = "SERIAL_CONNECTION_CLOSED"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            log.error(
                "BladderCommand : Error probably in responseStatus call or resource is busy"
            )

    def execute(self, responseStatusCallback, jsonObject):
        """Interface entry point to execute a bladder command.  Calls the appropriate helper depending on the command type.

        :param responseStatusCallback: Function to call after execution to send response to computer.

        :param jsonObject: json object representing the command to execute
        :type jsonObject: dict
        """
        try:
            jsonObject["response"] = "ACTION_OR_SELECT_FIELD_NOT_IN_JSON"
            if "action" in jsonObject:
                self._t1 = threading.Thread(
                    target=self._inflate_deflate,
                    args=(
                        responseStatusCallback,
                        jsonObject,
                    ),
                )
                self._t1.start()
                log.info("BladderCommand : Process bladder command")
                jsonObject["response"] = "PROCESS_BLADDER_COMMAND"

            if responseStatusCallback is not None:
                responseStatusCallback(jsonObject)
            else:
                print(jsonObject)
        except:
            log.error(
                "BladderCommand : Error no action or select field in json object"
            )

class Status(Enum):
    ERROR = -1
    INITIALIZED = 0
    MOVE_DIST = 1
    MOVE = 2
    STOPPED = 3
    END_STOPPED = 4
    WAITING = 5

# TODO select wait implementation that is most efficient

class BladderMotor(object):

    def __init__(self, address, mot, event, enc1=None, enc2=None):
        """
        __init__ Motor controller for motors in the inflatable bladder.

        :param address: Address of motorcontroller
        :type address: int
        :param mot: Motor selector
        :type mot: int
        :param event: Event for when motor is done with a movement
        :type event: Threading.event
        :param enc1: Encoder pin one, defaults to None
        :type enc1: int, optional
        :param enc2: Encoder pin two, defaults to None
        :type enc2: int, optional
        """
        self._address = address
        self.motor = qwiic_scmd.QwiicScmd(address)
        if enc1 and enc2:
            # Set up GPIOs for encoders
            GPIO.setup(enc1, GPIO.IN)
            GPIO.setup(enc2, GPIO.IN)
            self.A = enc1
            self.B = enc2
            # Variables to store distance moved
            self.pos = 0
            self.state = 0
            if GPIO.input(enc1):
                self.state |= 1
            if GPIO.input(enc2):
                self.state |= 2

            # Variables used for moving the motors a specified distance
            self.init_pos = 0
            self.distance_to_move = 0

            # Calback function for encoder pins
            GPIO.add_event_detect(enc1, GPIO.BOTH, callback=self.__update)
            GPIO.add_event_detect(enc2, GPIO.BOTH, callback=self.__update)

            self.dir = 0
            self.mot = mot
            self.addr = address

            self.motor.begin()
            self.motor.set_drive(self.mot, self.dir, 0)
            self.motor.enable()
            time.sleep(0.250)

            self.mEvent = event
            
            self.iEvent = threading.Event()
            self.timeout = None
            self.last_pos = 0

            self.status = Status.INITIALIZED
            log.debug(f"Initialized motor {self._address}-{mot} for the bladder")
        else:
            log.error(f"Failed to initialize a bladder motor")
            self.status = Status.ERROR

    def reset(self):
        self.stop()
        self.pos = 0
        self.init_pos = 0
        self.distance_to_move = 0
        self.state = Status.STOPPED

    def _reschedule(self):
        if self.timeout is None:
            return
        else:
            deadline = asyncio.get_running_loop().time() + config.MOTOR_TIMEOUT
            self.timeout.reschedule(deadline)

    async def wait(self):
        """
        wait wait for motor to finish moving, while checking 
        """
        try:
            async with asyncio.timeout(10) as self.timeout:
                self._reschedule()
                await(self.mEvent)
                self.state = "Finished"
        except TimeoutError:
            self.status = Status.END_STOPPED
            log.warning(f"Motor {self._address} was stopped due to lack of motion.")

    async def wait2(self):
        """
        wait2 Alternate wait implementation that may be more computationally efficient
        """
        self.iEvent.set()
        while not self.mEvent.is_set():
            try:
                async with asyncio.timeout(config.MOTOR_TIMEOUT):
                    await(self.mEvent)
            except TimeoutError:
                if self.iEvent.is_set():
                    self.iEvent.clear()
                else:
                    self.status = Status.END_STOPPED
                    log.warning(f"Motor {self._address} was stopped due to lack of motion.")
                    self.mEvent.set()

    async def wait3(self):
        """
        wait3 Alternate wait implementation that may be more computationally efficient
        """
        while not self.mEvent.is_set():
            try:
                async with asyncio.timeout(config.MOTOR_TIMEOUT):
                    await(self.mEvent)
            except TimeoutError:
                if self.pos == self.last_pos:
                    self.status = Status.END_STOPPED
                    log.warning(f"Motor {self._address} was stopped due to lack of motion.")
                    self.mEvent.set()
                else:
                    self.last_pos = self.pos


    def __update(self, channel):
        
        self.iEvent.set()
        self._reschedule()

        state = self.state & 3
        if GPIO.input(self.A):
            state |= 4
        if GPIO.input(self.B):
            state |= 8

        self.state = state >> 2

        if state == 1 or state == 7 or state == 8 or state == 14:
            self.pos += 1
        elif state == 2 or state == 4 or state == 11 or state == 13:
            self.pos -= 1
        elif state == 3 or state == 12:
            self.pos += 2
        elif state == 6 or state == 9:
            self.pos -= 2



        # Check if the motors need to stop
        if self.status == Status.MOVE_DIST:
            # print(self.addr, self.mot, self.pos)
            if abs(self.pos - self.init_pos) >= self.distance_to_move:
                self.stop()



    def set_direction(self, direction):
        if direction == "out" or direction == 1:
            self.dir = 1
        elif direction == "in" or direction == 0:
            self.dir = 0

    async def move_distance(self, direction, speed, distance):
        """
        move_distance Move a specified distance speed and direction.

        :param direction: Direction to move
        :type direction: _type_
        :param speed: Speed to move
        :type speed: int
        :param distance: Distance to move
        :type distance: int
        """
        self.status = Status.MOVE_DIST
        if self.A and self.B:
            self.init_pos = self.pos
            self.distance_to_move = distance
            self.set_direction(direction)
            self.motor.set_drive(self.mot, self.dir, speed)
            self.move(direction, speed)
        self.wait()

    def stop(self):
        """
        Stop the motor clear any remaining move distance, and reset the init pos.
        """
        self.status = Status.STOPPED
        self.motor.set_drive(self.mot, self.dir, 0)
        self.init_pos = 0
        self.distance_to_move = 0
        self.mEvent.set()

    def move(self, direction, speed):
        self.status = Status.MOVE
        self.set_direction(direction)
        self.motor.set_drive(self.mot, self.dir, speed)

    def enc_read(self):
        return self.pos


if __name__ == "__main__":
    obj = BladderCommand()
    obj.execute(None, {"select": [1, 0, 0], "action": "inflate"})
