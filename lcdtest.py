#!/usr/bin/env python
from signal import signal, SIGTERM, SIGHUP, pause
from RPLCD.i2c import CharLCD
import multiprocessing
import time
import requests
import random
import string
import json
import os
from dotenv import load_dotenv, dotenv_values
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# load_dotenv()
config = dotenv_values(".env.local")
macENV = config["MAC"]

print('env is ', config)
print(macENV)

spotifyURL = 'https://api.spotify.com/v1'
baseURL = 'http://127.0.0.1:5001/upnext-8f097/us-central1/app'
if not macENV:
    baseURL = 'https://us-central1-upnext-8f097.cloudfunctions.net/app'


def safe_exit(signum, frame):
    exit(1)


def write_to_lcd(lcd, string, num_cols):
    """Write the framebuffer out to the specified LCD."""
    lcd.home()
    # lcd.cursor_pos = (row, 0)
    print(string)
    lcd.write_string(string)


def displayString(lcd, num_cols, staticText="", string="", staticText2="", string2="", delay=0.5):

    framebuffer = ["", ""]

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
        i += 1
        k += 1
        if i == len(s) - num_cols:  # + len(staticText):
            i = 0 + len(staticText)
        if k == len(s2) - num_cols:  # + len(staticText2):
            k = 0 + len(staticText2)

        time.sleep(delay)

def displayLoginInfo(lcd, piCode):
    displayString(lcd, 16, 
        staticText="Your code: " + piCode, 
        string2="At upnext.mikalyoung.com")

def displayPlaybackInfo(conn2):
    # calls functions that start with display
    if not macENV:
        lcd = CharLCD('PCF8574', 0x27)
        lcd.clear()
        #piCode = conn2.recv()
        #displayLoginInfo(lcd, piCode)
        
    while True:
        #if not conn2.poll():
        #    return
        storedNowPlaying = ''
        data = conn2.recv()
        print(data)

        if macENV:
            continue
        
        if data["piCode"]:
            displayLoginInfo(lcd, data["piCode"])
            continue

        if storedNowPlaying == data["nowPlaying"]:
            continue
        
        storedNowPlaying = data["nowPlaying"]
        displayString(
            lcd, 16,
            staticText=data["staticText"],
            string=data["string"],
            staticText2=data["staticText2"],
            string2=data["string2"]
        )

def getNewAccessToken(refresh_token):
    try:
        return requests.get(baseURL + '/getToken', params = {
            "refresh_token": refresh_token
        }).json()
    except:
        return {}

def getHeaders(piCode):
    timeout = 3
    count = 0
    headers = ''

    # this section waits for the user to enter their code
    while True:
        try:
            headers = requests.get(headerEndpoint + piCode)
            headers.raise_for_status()
            headers = headers.json()
            return headers
        except:
            count += timeout
            if count % 15 == 0:
                print('miss')
            if  count >= 900: # 15 min wait time 
                safe_exit()
            time.sleep(timeout)

if __name__ == '__main__':
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    headerEndpoint = baseURL + '/getCode/'
    
    piCode = ''.join(random.choices(string.ascii_uppercase, k=5))
    piCode = 'mikal'

    try:
        # the user has entered their code 
        conn1, conn2 = multiprocessing.Pipe()
        lcdProcess = multiprocessing.Process(
            target=displayPlaybackInfo,
            args=(conn2,))
        lcdProcess.start()

        conn1.send({"piCode": piCode})
        headers = getHeaders(piCode)

        #run as long as the access token is valid
        while headers["access_token"]:
            headersString = {
                'Authorization': 'Bearer ' + headers['access_token'],
                'Content-Type': 'application/json'
            }
            # print(headersString)
            try:
                queue = requests.get(
                    spotifyURL + '/me/player/queue', headers=headersString).json()
                nowPlaying = requests.get(
                    spotifyURL + '/me/player/currently-playing', headers=headersString).json()
            except Exception as e:
                print('Exception has occured: ', e)
                if headers["exp"] < time.time():
                    headers = getNewAccessToken(headers["refresh_token"])
                else:
                    #display login info, block until valid
                    conn1.send({"piCode": piCode})
                    headers = getHeaders(piCode)

            try:
                nowPlaying = nowPlaying["item"]["name"]
                nextUp = queue["queue"][0]

                if nextUp:
                    nextUp = nextUp["name"]
                    print(nextUp, ' ', nowPlaying)
                    info = {
                        "string": "Now Playing: " + nowPlaying,
                        "string2": "Next Up: " + nextUp
                    }
                    conn1.send(info)
            except:
                print("nothing is playing at the moment")
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('Exception has occured: ', e)
        logger.exception(e)

    finally:
        if not macENV:
            lcd.clear()
