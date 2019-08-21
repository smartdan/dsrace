#!/usr/bin/env python 

import ftplib
import sys
import os
 
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