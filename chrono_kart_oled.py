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

import sys
import os
import datetime
import signal
import threading
import time
import traceback
from math import pi
from time import localtime, strftime
import stat
import logging
import arrow
import utm
from logging.handlers import RotatingFileHandler
import ftplib
import base64
import spidev as SPI
import EPD_driver
from oled_utils import OledUtils

from chronograph.chronograph import Chronograph

from gps import *
from shapely.geometry import Point, Polygon, LineString

'''
###############################
            Get split
##############################
'''
def doSplit(test_point = None, speed = None):
    '''
        Get split
        test_point, speed

        get error e(i) = speed * distance_from_finish
        
        LAP TIME
        time = t(i) - e(i) + e(i-1) 
    '''

    global cg
    global laps
    global count
    global new_min
    global BEST_lap
    global lap_starting
    global filename
    global current_lap
    global name 
    global finish_line
    global corrections

    if current_lap < 15:
        return
    else:
        cg.split("Lap")
        lap_starting = cg.total_elapsed_time
    
    e_i = 0
    count += 1

    # Handle positioning error
    if test_point and speed:
        if speed > 0:
            test_utm_point = utm.from_latlon(test_point.x, test_point.y)
            utm_point = Point(test_utm_point[0], test_utm_point[1])
            dist = utm_point.distance(finish_line);
            #speed in m/s, distance in m => error_time in seconds
            e_i =  dist / speed 
            print 'CORRECTIONS err, dist, speed: ', str(e_i), str(dist), str(speed)
            log.info('CORRECTIONS err, dist, speed: ' + str(e_i) + ' ' + str(dist) + ' ' + str(speed))

            corrections.append(e_i)
            #estimated lap time = t(i) - e(i) + e(i-1)
            estimatedlap = cg.last_split_time - corrections[-1]

            if len(corrections) > 1:
                estimatedlap += corrections[-2]
                print "CORRECTED s, c1, c2, el ", str(cg.last_split_time), str(corrections[-1]), str(corrections[-2]), str(estimatedlap)
                log.info("CORRECTED split, e1, e2, estimated lap " + str(cg.last_split_time) + " " + str(corrections[-1]) + " " + str(corrections[-2]) + " " + str(estimatedlap))
            
            laps.append(estimatedlap)
        else:
            log.info('SPEED NEGATIVE: ' + str(speed))
            laps.append(cg.last_split_time)        
    else:
        laps.append(cg.last_split_time)

    c_min = min(laps)

    if c_min < new_min:
        new_min = c_min
        BEST_lap = laps.index(new_min) + 1

    # Recognize another session
    if laps[-1] > 500 and count > 2:  
        log.info('Starting a new session')
        clap = laps[-1]
        laps = []
        laps.append(clap)
        corrections = []
        corrections.append(e_i)
        count = 2
        new_min = clap
        BEST_lap = 1
        now = arrow.now('Europe/Rome').format('(DD/MM/YY HH:mm)')
        with open(filename, 'a') as the_file:        
            the_file.write('# SESSIONE ' + now + ' (versione ' + version +') \n')
            the_file.write('# ' + name + ' ' + now + '\n')
            the_file.write('# GPS STATUS ' + str(gpsd.status) + '\n')
            the_file.write("" + str('{0:.2f}'.format(laps[-1])) + " - " + name + " - GIRO " + str(count - 1) + '\n')
    else:
        with open(filename, 'a') as the_file:
            the_file.write("" + str('{0:.2f}'.format(laps[-1])) + " - " + name + " - GIRO " + str(count - 1) + '\n')
    
    update_screen()  
    
'''
###############################
            LOOP METHODS
###############################
'''

def startChrono():
    ''' START THE CHRONOGRAPH '''

    global cg
    global laps
    global L_lcd
    global count
    global lap_starting
    global current_lap

    cg.reset()
    cg.start("first lap")

    while True:    # infinite loop
        try:
            current_lap = cg.total_elapsed_time - lap_starting

            time.sleep(0.005)

            if to_stop == 1:
               print("TO STOP CHRONO")
               break
        except Exception:
            log.info('Error in chrono')
            pass

def startTracker():
    ''' START THE GPS TRACKER '''

    global gpsd
    global in_polygon
    global gpswaiting
    global cg
    global polygon
    global filename

    testcounter = 0   

    try:
       while True:
           gpswaiting = True
           gpsd.next() 
           gpswaiting = False

           #logFix(gpsd) 
           #if(gpsd.fix.speed < gpsd.fix.eps or gpsd.fix.speed < 3):
           #    print 'Speed with no accuracy', str(gpsd.fix.speed), str(gpsd.fix.eps) 
           
           if gpsd.fix.latitude != 0 or gpsd.fix.longitude != 0:
               
               testpoint = Point(gpsd.fix.longitude, gpsd.fix.latitude)               
               contains = polygon.contains(testpoint)
               
               if contains == True and in_polygon == False:
                   in_polygon = True
                   log.info("IN POLYGON!")
                   logFix(gpsd)
                   if(gpsd.fix.speed < gpsd.fix.eps or gpsd.fix.speed < 3):
                       print 'Speed with no accuracy', str(gpsd.fix.speed), str(gpsd.fix.eps) 
                   
                   #doSplit()
                   testspeed = gpsd.fix.speed

                   # speed with no accuracy
                   if(gpsd.fix.speed < 3): #10km/h
                       testspeed = 0

                   doSplit(testpoint, testspeed)
               elif contains == False:
                   in_polygon = False                    

           time.sleep(0.005) 

           if to_stop == 1:
               print("TO STOP TRACKER")
               break
    except Exception:
        log.info('Error in tracker')
        pass

def logFix(gpsd):
    try:
        log.info('GPS FIX')
        log.info('status      ' + str(gpsd.status))
        log.info('latitude    ' + str(gpsd.fix.latitude))
        log.info('longitude   ' + str(gpsd.fix.longitude))
        log.info('speed       ' + str(gpsd.fix.speed))
        log.info('sats        ' + str(len(gpsd.satellites)))
        log.info('epx         ' + str(gpsd.fix.epx))
        log.info('epy         ' + str(gpsd.fix.epy))
        log.info('eps         ' + str(gpsd.fix.eps))
        log.info('            ')     
    except:
        log.warning('Error fix')

def file_age_in_seconds(pathname):
    if os.path.isfile(pathname) == False:
        return 0
    
    #print str(time.time())
    #print str(os.stat(pathname)[stat.ST_MTIME])
    return time.time() - os.stat(pathname)[stat.ST_MTIME]


def update_screen():
    global oledUtils
    global cg
    global count
    global laps
    global new_min
    global BEST_lap
    global current_lap
  
    try:
        #CURRENT
        current_time = str('{0:.2f}'.format(current_lap))     
        text = 'C {0} {1}'.format(str(count), current_time)
        line_current = '{0: <16}'.format(text)

        #LAST
        LAST = ''
        try:
            LAST = str('{0:.2f}'.format(laps[-1]))
        except:
            LAST = ''
        line_last = "L " + LAST + " s:" + str(count - 1)
    
        #BEST
        show_min = -1
        if(new_min < 10000000000000):
            show_min = new_min
        
        min_f = str('{0:.2f}'.format(show_min))
        line_best = "B " + min_f + " s:" + str(BEST_lap)

        #UPDATE LINES
        print '------------Show lines------------'
        oledUtils.resetLcd()
        oledUtils.writeFirst(line_current)
        oledUtils.writeSecond(line_last)
        oledUtils.writeThird(line_best)

    except Exception as e:
        print 'Error in chrono ', str(e)


'''
###################################################################
###################### MAIN APP - DS CHRONOGRAPH ##################
###################################################################
'''
# GLOBALS
version = '0.3.6'
gpsd = None
gpswaiting = False 
count_cron = 0
count = 1
new_min = 10000000000000
BEST_lap = 0
to_stop = 0
lap_starting = 0
current_lap = 0
t1 = threading.Thread(target=startChrono)
t3 = threading.Thread(target=startTracker)
current_path = os.path.dirname(__file__) + '/'
name = sys.argv[1]


log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = current_path + 'chrono_' + name + '.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
log = logging.getLogger('root')
log.setLevel(logging.INFO)
log.addHandler(my_handler)

log.debug('STARTING CHRONO...')

#PM RACING FINISH LINE 
polygon1 = Polygon([(7.423350,45.087818), 
                   (7.423473,45.087712), 
                   (7.423354,45.087662), 
                   (7.423221,45.087767), 
                   (7.423350,45.087818)])

# PRISMA 88 
polygon2 = Polygon([(7.508262,45.080289),
                   (7.508355,45.080262),
                   (7.508341,45.080241), 
                   (7.508252,45.080269),
                   (7.508262,45.080289)])
 
#polygon = polygon2
#log.info('Polygon PRISMA set')

polygon = polygon1
log.info('Polygon PM RACING set')

# utm points for finish line
f1_1 = utm.from_latlon(7.423235,45.087766)
f2_1 = utm.from_latlon(7.423321,45.087820)

'''
f1_1 = utm.from_latlon(7.423350,45.087818)
f2_1 = utm.from_latlon(7.423221,45.087767)
'''

# utm line string
finish_1 = LineString([Point(f1_1[0],f1_1[1]), 
                       Point(f2_1[0],f2_1[1])])

#real finish line
finish_line = finish_1

oledUtils = OledUtils()
oledUtils.resetLcd()

try:
    os.system('sudo /etc/init.d/ntp stop')
    os.system('sudo ntpd -q -g')
    os.system('sudo /etc/init.d/ntp start')
    os.system('sudo killall gpsd')
    os.system('sudo gpsd /dev/ttyACM0 -F /var/run/gpsd.sock')
    # Set GPS Frequency to 10HZ
    print 'Set 10 HZ'
    os.system('sudo gpsctl -c 0.1')       
    time.sleep(2)
    os.system('sudo ntpd -gN')
    time.sleep(2)
    in_polygon = False
    filename = current_path + name + '.txt'
    cg = Chronograph(name="Kart Chronograph")
    laps = []    
    corrections = []
    count = 1
    new_min = 10000000000000
    BEST_lap = 0
    to_stop = 0
    in_polygon = False
    
    count_cron += 1
    log.info("Starting " + str(count_cron) + "...")

    now = arrow.now('Europe/Rome').format('(DD/MM/YY HH:mm)')
    print(now)

    age = file_age_in_seconds(filename) / 3600
    log.info("File age in hours: " + str(age))

    if(age > 12):
        log.info("Remove file " + filename)
        os.system("sudo rm -f " + filename)

    log.info("SESSION " + now)

    #ePAPER
    print 'SESSION ON DISPLAY'
    oledUtils.writeFirst('S ' + now + ' (v. ' + version +')')

    with open(filename, 'a') as the_file:        
       the_file.write('# SESSIONE ' + now + ' (versione ' + version +') \n')
       the_file.write('# ' + name + ' ' + now + '\n') 

    #starting the stream of info from GPS
    gpsd = gps(mode=WATCH_ENABLE)   
    testcounter = 0   
    gpsd.next()
    
    with open(filename, 'a') as the_file:        
       the_file.write('# GPS STATUS ' + str(gpsd.status) + '\n')
    
    log.info("Starting threads")
    t1 = threading.Thread(target=startChrono)
    t1.start()

    t3 = threading.Thread(target=startTracker)
    t3.start()

    log.info("Threads are running")
    
    #CALL FTP LOOP 
    while(1):
        try:
            update_screen()   
            logFix(gpsd) 

            #log.info('Call upload_file
            os.system("sudo python "+ current_path + "upload_file.py " + name)
            #log.info("Sent File to FTP")                    
        except:
            log.warning('Error upload_file')

        time.sleep(30)

    # Prevent the script exiting!
    signal.pause()

except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nExiting...")
    to_stop = 1
    t1.join()
    t3.join()
    sys.exit()
