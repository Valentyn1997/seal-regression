#!/bin/bash

sudo apt-get update
sudo apt-get install g++ git make python3 python3-dev python3-pip sudo libdpkg-perl
sudo rm -rf PySEAL/
sudo git clone https://github.com/Lab41/PySEAL.git
sudo rm -rf /SEAL/
sudo mkdir -p /SEAL/
sudo cp -r PySEAL/SEAL/ /SEAL/SEAL/
sudo cp -r PySEAL/SEALPython/ /SEAL/SEALPython/
sudo rm -rf PySEAL/

# C++ SEAL package
cd /SEAL/SEAL/
sudo chmod +x configure
sudo sed -i -e 's/\r$//' configure
sudo ./configure
sudo make

# PySEAL package
cd /SEAL/SEALPython/
sudo pip3 install -r requirements.txt
sudo rm -rf pybind11/
sudo git clone https://github.com/pybind/pybind11.git
sudo python3 setup.py install