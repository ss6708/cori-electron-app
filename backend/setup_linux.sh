#!/bin/bash
# Setup script for Linux dependencies

# Update package lists
sudo apt-get update

# Install LibreOffice Calc and Python UNO bridge
sudo apt-get install -y libreoffice-calc python3-uno libreoffice-script-provider-python

# Install xdotool for window management
sudo apt-get install -y xdotool
