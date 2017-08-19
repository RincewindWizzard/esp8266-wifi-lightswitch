#!/bin/sh
#ampy --port /dev/ttyUSB0 run lightswitch.py
ampy -b 115200 --port /dev/ttyUSB0 put lightswitch.py