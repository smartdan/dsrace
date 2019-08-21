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

current_path = os.path.dirname(__file__) + '/'
ftp_connection = ftplib.FTP(server, username, password)
remote_path = "/htdocs/dsrace"
ftp_connection.cwd(remote_path)

try:
    name = sys.argv[1]
    fh1 = open(current_path + name + ".txt", 'rb')
    ftp_connection.storbinary('STOR ' + name + '.txt', fh1)
    fh1.close()
finally:
    print "Sent File"