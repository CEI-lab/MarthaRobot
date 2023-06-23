#!/bin/sh

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")

PATH=$HOME/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
PYTHONPATH=$PYTHONPATH:/usr/local/lib

cd $HOME/HSI/
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority
echo "raspberry" | sudo -S python3  -m robot #> $HOME/HSI/output 2>&1
