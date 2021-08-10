#!/bin/sh
PATH=$HOME/bin:$HOME/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
cd $HOME/HSI/
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority
echo "raspberry" | sudo -S python3 $HOME/HSI/HSIMaster.py #> $HOME/HSI/output 2>&1
