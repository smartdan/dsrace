#!/usr/bin/env python 

'''
 Copyright 2017 Daniele Sabetta

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
import ftplib
import sys
import os
import base64
 
server = 'ftp.xxxxxxxx.it'
username = 'xxxxxxxxx.it'
password = 'xxxxxxxxxx'

my_path = '/home/pi/DSRace/'
ftp_connection = ftplib.FTP(server, username, password)
remote_path = "/htdocs/dsrace"
ftp_connection.cwd(remote_path)
filename = 'chrono_kart.py'
filename_temp = 'temp.py'

try:
    ftp_connection = ftplib.FTP(server, username, password)   
    ftp_connection.cwd(remote_path)
    ftp_connection.retrbinary("RETR " + filename , open(my_path + filename_temp, 'wb').write)
    ftp_connection.quit()
    os.rename(my_path + filename_temp, my_path + filename)
except Exception as e:
    print "FILE NOT FOUND OR ERROR", e