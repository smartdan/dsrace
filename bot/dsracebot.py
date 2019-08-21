#!/usr/bin/env python

'''
MIT License

Copyright (c) 2017 Daniele Sabetta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
#IMPORT
import time
import random
import datetime
import telepot
import os
import subprocess
import urllib
import ftplib
import sys

###HANDLE MESSAGE###
def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    command = ''
    
    if content_type == 'text':
        command = msg['text']

    name = ''
    surname = ''

    try:
        #Parse incoming message
        if(chat_type == 'private'):
            name = msg['chat']['first_name']
            surname = msg['chat']['last_name']
            print 'Private chat with {} {}'.format(name, surname)  
        else:
            name = msg['chat']['title']
            command = command.replace('@botname','')

        #Get user details
        user = msg['from']
        if user is not None:
            name = user['first_name']
            surname = user['last_name']
            print 'User: {} {}'.format(name, surname)  

        #Log command
        print('Comando ricevuto: %s' % command)

        #Handle message
        if (name == 'XXX' and surname == 'XXX'):       
            answer(chat_id, command, name, surname)
        else:
            if(command.startswith( '/' )):
                bot.sendMessage(chat_id, 'In fase di test. Visualizza i dati dei tempi su http://www.xxxxxxxxx.it/race')
            
    except Exception as e:
        print e 
        bot.sendMessage(chat_id, 'Non sei autorizzato. ')
        bot.sendMessage(chat_id, 'Visualizza i risultati dei tempi su http://www.xxxxxxxxxx.it/race')


#### METHODS ####
def downloadFile(filename):
    global my_path
    global remote_path

    try:
        ftp_connection = ftplib.FTP(server, username, password)   
        ftp_connection.cwd(remote_path)
        ftp_connection.retrbinary("RETR " + filename ,open(my_path + filename, 'wb').write)
        ftp_connection.quit()
    except Exception as e:
        print "FILE NOT FOUND OR ERROR", e


def downloadFiles():
    global my_path
    global remote_path
    
    ftp_connection = ftplib.FTP(server, username, password)  
    ftp_connection.cwd(remote_path)
    
    for number in range(1,11): 
        ftp_connection.retrbinary("RETR kart_" + str(number) +  ".txt" ,open(my_path + "kart_" + str(number) + ".txt", 'wb').write)

    ftp_connection.quit
    
def readfile(filename):
    global my_path
    header = []
    laps = []
    downloadFile(filename)

    try:
        with open(my_path + filename) as f:
            lines = f.readlines()
            last_session_idx = 0

            try:
                last_session_idx = max(loc for loc, val in enumerate(lines) if 'SESSION' in val)
                print "INDEX LAST SESSION ", last_session_idx
            except:
                pass

            idx = 0

            for line in lines:
                if idx < last_session_idx:
                    idx += 1              
                    continue

                if line.startswith("#") or line.startswith("'''"):
                    header.append(line)
                else:
                    if len(line) > 2:
                        laps.append(line)

    except Exception as e:
        print "FILE NOT FOUND OR ERROR", e

    return laps, header

def getTextForAnswer(num):
    filename = "kart_" + str(num) + ".txt"
    laps, header = readfile(filename)
    text = ""
    text += "".join(header)
    text += "".join(laps)
    return text

def getBestLaps():
    bestlaps = []

    for number in range(1,11): 
        laps, header = readfile("kart_" + str(number) + ".txt")
        if len(laps) > 0:
            min_lap = -1
            index = 0
            counter = 0
            for lap in laps:
                val = float(lap.split(' ')[0].replace("\n",""))
                if min_lap < 0 or val < min_lap:
                    min_lap = val         
                    index = counter
                counter += 1
            best = (laps[index] + " " + header[0].replace("\n","")).replace("# SESSIONE","").replace(" # SESSION","")

            bestlaps.append((best, min_lap))

    bestlaps.sort(key=lambda tup: (tup[1]))

    print bestlaps

    return bestlaps

def getLapsTuple():
    tupleLaps = []

    for number in range(1,11): 
        kart = "kart_" + str(number)
        laps, header = readfile(kart + ".txt")
        num_laps = len(laps)
        if num_laps > 0:            
            times = []

            for lap in laps:
                try:
                    lap_str = lap.split(' ')[0].replace("\n","").strip()
                    #print lap_str
                    val = float(lap_str)
                    times.append(val)
                except Exception as e:
                    print "Error: ", e

            time = sum(times[:-1])
            tupleLaps.append((kart, num_laps - 1, time))

    tupleLaps.sort(key=lambda tup: (-tup[1],tup[2]))

    print tupleLaps

    return tupleLaps

def answer(chat_id, command, name, surname):
    global session_filename
    global race_filename

    if command == '/race':
        bot.sendMessage(chat_id, "Classifica della gara in elaborazione...")
        text = ""
        lines = []

        #downloadFiles()
        tupleLaps = getLapsTuple()
        
        lines.append("CLASSIFICA GARA")    
        lines.append("")

        for idx, (kart, num_laps, time) in enumerate(tupleLaps):
            if time > 0:
                lines.append(str(idx + 1) + ") " + kart + " - " + str(num_laps) + " giri in " + str(time) + " sec." )

        text += "\n".join(lines)
        bot.sendMessage(chat_id, text)
        bot.sendMessage(chat_id, "Giro di uscita escluso dal conteggio.")

        #FTP UPLOAD
        try:
            with open(race_filename, 'w') as the_file:        
                the_file.write(text)
            
            os.system("sudo python " + my_path + "upload_file.py race")
        except Exception as e:
            print e 
            print 'Error upload_file'
    elif command == '/session':
        bot.sendMessage(chat_id, "Classifica ultima sessione in elaborazione...")
        text = ""
        lines = []

        #downloadFiles()
        bestlaps = getBestLaps()
        
        lines.append("CLASSIFICA SESSIONE")    
        lines.append("")

        for idx, (val, time) in enumerate(bestlaps):
            lines.append(str(idx + 1) + ") " + val)

        text += "\n".join(lines)
        bot.sendMessage(chat_id, text)

        #FTP UPLOAD
        try:
            with open(session_filename, 'w') as the_file:        
                the_file.write(text)
            
            os.system("sudo python " + my_path + "upload_file.py session")
        except Exception as e:
            print e 
            print 'Error upload_file'

    elif command.startswith("/kart_"):     
        num = command.replace("/kart_", "")        
        bot.sendMessage(chat_id, getTextForAnswer(num))   
    elif command == '/start':
        bot.sendMessage(chat_id, 'ciao ' + name + "!")
        bot.sendMessage(chat_id, 'Visualizza i risultati dei tempi su http://www.xxxxxxxxxxxx.it/race')
    else:
        bot.sendMessage(chat_id, 'Non ho capito.')

######### MAIN LOOP
remote_path = "/htdocs/pmrace"
my_path = os.path.dirname(__file__) + '/'
session_filename = my_path + "session.txt"
race_filename = my_path + "race.txt"
bot = telepot.Bot('#######ID_BOT_FROM_BOTFATHER###########')
bot.message_loop(handle)

server = 'ftp.xxxxxxxx.it'
username = 'xxxxxxxxx.it'
password = 'xxxxxxxxxx'
print('Bot is starting ...')

while 1:
    time.sleep(10)