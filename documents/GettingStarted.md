# Turning on the rover

<!-- TODO battery type -->

To turn on the rover simply plug a battery () in.

# Connecting to the rover

## Finding IP with GUI/Display

Either open a shell and use `ifconfig` or hover the mouse over the network icon in the top right.

## Finding IP without display

If you cannot connect a display to the RPi, the easiest method of connecting is a direct ethernet connection between your computer and the RPi. You can use this connection to ssh into the RPi and setup wifi using `sudo raspi-config` or find the current IP address with the `ifconfig` command.

# Working on the rover

I recommend using Visual Studio Code to work on the robot. It will allow you to edit files over ssh with all the amenities of a modern IDE. You can also open multiple terminals/shells on the RPi through the same window.

The rover is primarily operated by sending commands from a base computer to the rover. This allows more for complex computations and remote control.

[Client.py](../client/Client.py) provides a REPL interface for sending manual commands to the rover.

Before sending commands, you will need to run [start-robot.sh](../start-robot.sh) on the RPi.
