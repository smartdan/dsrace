#!/usr/bin/env python 

'''
Script per la connessione ad una WIFI via terminale
Usage: sudo ./connect_wifi.py ssid pwd
'''
import sys
import os

name = ""
password = ""

if len(sys.argv) == 3:
    name = sys.argv[1]
    password = sys.argv[2]
else:
    sys.exit()

os.system('sudo ifconfig wlan0 up')
os.system('sudo iwconfig wlan0 essid ' + name + ' key s:' + password)
os.system('sudo dhclient wlan0')


