#bin/bash

/home/pi/HSI/marthabot/robot/commands/set_speed/SmcCmd/SmcCmd -d 52FF-6B06-8365-5650-2936-2167  $1 &
/home/pi/HSI/marthabot/robot/commands/set_speed/SmcCmd/SmcCmd -d 52FF-6C06-8365-5650-4238-2167 $2 &

#This file was written by:
#   /home/pi/HSI/marthabot/robot/commands/set_speed/set_speed_command.py
#It is meant to make it easier to send commands to both motors (semi) simultaneously