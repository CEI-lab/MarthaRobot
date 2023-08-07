# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import os

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c, mode = ADS.Mode.SINGLE)
# you can specify an I2C adress instead of the default 0x48
# ads = ADS.ADS1115(i2c, address=0x49)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P0)


# chan2 = AnalogIn(ads, ADS.P1)

# Create differential input between channel 0 and 1
# chan = AnalogIn(ads, ADS.P0, ADS.P1)



def v2capacity(voltage):
    max_v = 3.3
    min_v = 2.9
    min_c = 0.1
    range_v = max_v - min_v
    c = (voltage - min_v) / range_v
    return c + min_c

lowcount = 0
while True:
    # print("-----")
    cap = v2capacity(chan.voltage)

    # print("{:>5}\t{:>5.3f}".format(chan.value, v2capacity(chan.voltage)))
    # print("{:>5}\t{:>5.3f}".format(chan.value, v2capacity(chan2.voltage)))
    if cap < 0.2:
        lowcount += 1
    else:
        lowcount = 0
    
    print(f"{time.asctime()}: {cap}%")

    if lowcount > 5:
        print("WARNING")
        print("Low voltage detected, shutting down.")
        time.sleep(5)
        os.system("shutdown /s /t 1")

    if lowcount:
        time.sleep(10)
    else:
        time.sleep(30)
    
