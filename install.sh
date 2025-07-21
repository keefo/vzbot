#!/bin/bash

# git clone https://github.com/dw-0/kiauh.git
# git clone https://github.com/keefo/vzbot.git

cd ~/

# update
sudo apt update 
sudo apt upgrade -y
sudo apt install python3-spidev
sudo apt install python3-venv

# install klipper
git clone https://github.com/Klipper3d/klipper.git
git clone https://github.com/Arksine/moonraker.git
git clone 
# install moonraker

ls /dev/serial/by-id/*


# sudo service klipper stop 
# make flash FLASH_DEVICE=/dev/serial/by-id/usb-Klipper_stm32h723xx_4A0018001651313338343730-if00
# sudo service klipper start

# mcu chip
# STM32H723ZG1b

# Put super8 board into DFU mode by using jumper 
# Connect super8 pro board to computer via USB
# Use STM32CubeProgrammer.app to flash the firmware


# install beacon
git clone https://github.com/beacon3d/beacon_klipper.git
./beacon_klipper/install.sh

# Beacon setup

BEACON_AUTO_CALIBRATE


# instal KAMP

 cd ~/
 
 git clone https://github.com/kyleisah/Klipper-Adaptive-Meshing-Purging.git
 ln -s ~/Klipper-Adaptive-Meshing-Purging/Configuration printer_data/config/KAMP
 cp ~/Klipper-Adaptive-Meshing-Purging/Configuration/KAMP_Settings.cfg ~/printer_data/config/KAMP_Settings.cfg
 
 sudo service klipper restart

# LED

# WS2814 DC12V 24V Led Strip Light 4 in 1 Similar SK6812 RGBW Pixels Addressable WS2811 RGBWW RGBCW 5050 3 Pin Lights IP30 65 67
mkdir ~/led
cp led/led.py ~/led/led.py
cd ~/led
python3 -m venv venv --system-site-packages
source venv/bin/activate
pip install rpi_ws281x adafruit-circuitpython-neopixel

pip uninstall rpi_ws281x adafruit-circuitpython-neopixel

# https://github.com/adafruit/Adafruit_Blinka_Raspberry_Pi5_Neopixel
pip install Adafruit-Blinka-Raspberry-Pi5-Neopixel
pip install Adafruit_CircuitPython_LED_Animation
