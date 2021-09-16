from __future__ import print_function
import time
import sys
import math
import qwiic_scmd

motor_3 = qwiic_scmd.QwiicScmd(0x5E)
motor_1_2 = qwiic_scmd.QwiicScmd(0x5E)

MOTOR_A = 0
MOTOR_B = 1
FWD = 0
BWD = 1

def runExample():
    print("Motor Test.")
    
#     if motor_1_2.connected == False:
#         print("Motor Driver 1 not connected. Check connections.", \
#             file=sys.stderr)
#         return
    if motor_3.connected == False:
        print("Motor Driver 2 not connected. Check connections.", \
            file=sys.stderr)
        return
#     motor_1_2.begin()
    motor_3.begin()
    print("Motors initialized.")
    time.sleep(.250)
    
    # Zero Motor Speeds
#     motor_1_2.set_drive(0,0,0)
#     motor_1_2.set_drive(1,0,0)
    motor_3.set_drive(0,0,0)
    motor_3.set_drive(1,0,0)
    
#     motor_1_2.enable()
    motor_3.enable()
    print("Motors enabled")
    time.sleep(.250)

    while True:
        speed = 250 # from 0-255
#         motor_1_2.set_drive(MOTOR_A,FWD,speed)
#         motor_1_2.set_drive(MOTOR_B,FWD,speed)
        motor_3.set_drive(MOTOR_B,FWD,speed)
#         time.sleep(3)
#         motor_1_2.set_drive(MOTOR_A,BWD,speed)
#         motor_1_2.set_drive(MOTOR_B,BWD,speed)
#         motor_3.set_drive(MOTOR_A,BWD,speed)
#         time.sleep(3)

if __name__ == '__main__':
    try:
        runExample()
    except (KeyboardInterrupt, SystemExit) as exErr:
        print("Ending example.")
#         motor_1_2.disable()
        motor_3.disable()
        sys.exit(0)
