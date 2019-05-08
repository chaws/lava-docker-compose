#!/bin/bash

# https://stackoverflow.com/questions/27858041/oserror-errno-13-permission-denied-dev-ttyacm0-using-pyserial-from-pyth
filename=arduino.rules
cat > /tmp/$filename <<EOM
KERNEL=="ttyACM0", MODE="0666"
EOM
sudo cp /tmp/$filename /etc/udev/rules.d/

# https://unix.stackexchange.com/questions/39370/how-to-reload-udev-rules-without-reboot
sudo udevadm control --reload-rules
sudo udevadm trigger
