# Common Issues

## Projector wont turn on

The projector is not powered by the robot so it must be charged seperately. The charging port is on the back of the projector.

## Projector turns on, but no image

Check that the hdmi cable is connected from the RPi to the projector. Test with different projectors or monitors to confirm if there is an issue with the cable/projector. Some RPis are configured to not display anything.

## Cannot connect to RPi

Make sure that you have the right IP address - they can change occasionally (see [getting started](getting-started.md) for instructions). Also make sure that the RPi is powered on, and that both the RPi and your computer are connected to the same wifi network.

It is possible that some networks may be configured to block the current connection methodology, so consider contactingi IT. If you are relying on the Cornell Visitor network keep in mind that you need to manually reconnect to the network every day.

If you have setup remote viewer software you can also try to connect through it.

## Hardware Malfunctions

Often if a motor or sensor is not behaving as expected it may indicate that the [configurations.py](../robot/configurations.py) does not match the robot's construction.

Pay attention for messages when you first run [start-robot.sh](../start-robot.sh) in case any of the hardware addresses are wrong.

Compare the pins declared in [configurations.py](../robot/configurations.py) to what is actually plugged in on the robot.

Otherwise consider software issues, or damaged components.
