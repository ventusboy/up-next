#!/usr/bin/env python
from signal import signal, SIGTERM, SIGHUP, pause
from RPLCD.i2c import CharLCD
import multiprocessing
import time
import requests
import random, string, json, os

macENV = os.environ.get('MAC')
spotifyURL = 'https://api.spotify.com/v1'

def safe_exit(signum, frame):
    exit(1)

def write_to_lcd(lcd, string, num_cols):
    """Write the framebuffer out to the specified LCD."""
    lcd.home()
    #lcd.cursor_pos = (row, 0)
    print(string)
    lcd.write_string(string)

def displayString( lcd, num_cols, staticText="", string="", staticText2="", string2="", delay=0.5):
    
    framebuffer = ["",""]

    padding = ' ' * num_cols
    s = padding + string + padding
    s2 = padding + string2 + padding
    
    longest = max(len(s), len(s2))
    
    i = num_cols
    k = num_cols
    while True:
        
        framebuffer[0] = staticText + s[i:i+num_cols - len(staticText)]
        framebuffer[1] = staticText2 + s2[k:k+num_cols - len(staticText2)]
        
        joinedString = framebuffer[0] + "\r\n" + framebuffer[1]
        write_to_lcd(lcd, joinedString, num_cols)
        i+=1
        k+=1
        if i == len(s) - num_cols : #+ len(staticText):
            i = 0 + len(staticText)
        if k == len(s2) - num_cols : #+ len(staticText2):
            k = 0 + len(staticText2)
        
        time.sleep(delay)    
try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    headerEndpoint = 'http://127.0.0.1:5001/upnext-8f097/us-central1/app/getCode/'
    if not macENV:
        headerEndpoint = 'https://us-central1-upnext-8f097.cloudfunctions.net/app/getCode/'
    long_string = 'Feel The Volume - JAUZ'
    long_string2 = 'The Calling - Tchami'

    piCode = ''.join(random.choices(string.ascii_uppercase, k=5))
    piCode = 'mikal'
    print(piCode)
    if not macENV:
        lcd = CharLCD('PCF8574', 0x27)
        lcd.clear()
        displayString(lcd, 16, staticText="Your code: " +  piCode, string2 = "At upnext.mikalyoung.com")
    timeout = 3
    count = 0
    headers = ''
    #time.sleep(timeout)
    while True:
        headers = requests.get(headerEndpoint + piCode).json()
        #if type(headers) == 'dict':
            #header = json.load(header)
        #print(headers)
        count += timeout
        if count%15 == 0:
            print('miss')
        if headers["access_token"] or count >= 900 : #15 min wait time
            print(headers)
            break
        time.sleep(timeout)

    #displayString(lcd, 16, "Now Playing:", long_string, "Next Up:", long_string2)
    """for x in headers:
        headers[x] = str(headers[x])"""
    while headers["access_token"]:
        #headersString = json.dumps(headers)
        headersString = {
            'Authorization': 'Bearer ' + headers['access_token'],
            'Content-Type': 'application/json'
        }
        #print(headersString)
        queue = requests.get(spotifyURL + '/me/player/queue', headers = headersString).json()
        nowPlaying = requests.get(spotifyURL + '/me/player/currently-playing', headers = headersString).json()
        print(nowPlaying)
        try:
            print(nowPlaying["item"]["name"])
            nowPlaying = nowPlaying["item"]["name"]
            nextUp = queue["queue"][0]
            if nextUp:
                nextUp = ["name"]
            if not macENV:
                displayString(lcd, 16, string="Now Playing: " + nowPlaying, string2="Next Up: " + nextUp)
                #displayString(lcd, 16, staticText="Your code: " +  piCode, string2 = "At upnext.mikalyoung.com")
        except:
            print("nothing is playing at the moment")
        time.sleep(10)
except KeyboardInterrupt:
    pass
finally:
    if not macENV:
        lcd.clear()

