# boiler-control-demo
Example code to set the water temperature of a boiler written in python. Can be run on a Raspberry Pi for example.
Has been successfully tested with a Vaillant ecoTEC Plus.

# Installation
Prerequisites:
1) You need a Canique Gateway and a Canique Heat Control device - as of Feb 2021 available on request from https://www.canique.com

2) You need Python 3. Code has been tested with Python 3.7.3 and gmqtt library 0.6.9 on a Raspberry Pi 3.
Code should run on any computer if you have a Python 3 environment.

To install gmqtt, run:
pip3 install gmqtt

# Usage
python3 /usr/local/bin/cnq-set-boiler-temperature.py GW-IP TEMPERATURE

GW-IP is the IP address of your Canique Gateway

TEMPERATURE is the boiler temperature that you want to set

Example Usage: python3 /usr/local/bin/cnq-set-boiler-temperature.py 192.168.10.233 50

This will set the temperature of your boiler to 50°C.
