#!/bin/bash

# Change current directory to project directory. 
CURRENT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $CURRENT_PATH

# Install PYQT4
sudo add-apt-repository ppa:rock-core/qt4
sudo apt update
sudo apt install libqt4-declarative libqt4* libqtcore4 libqtgui4 libqtwebkit4 qt4*


# Check version of pip
# Version must be below 18.XX and compatible with Python 3.4+
pip --version

# Install dependencies
pip3 install bs4 matplotlib
