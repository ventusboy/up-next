#!/usr/bin/env python
import time, os, json, string, random, multiprocessing
import requests, logging
from lcdController import LCDController

from signal import signal, SIGTERM, SIGHUP, pause
from dotenv import load_dotenv, dotenv_values #pip install python-dotenv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

config = dotenv_values(".env.local")

HAS_LCD = False
if 'HAS_LCD' in config:
    HAS_LCD = config["HAS_LCD"]

spotifyURL = 'https://api.spotify.com/v1'
baseURL = 'http://127.0.0.1:5001/upnext-8f097/us-central1/app'
if HAS_LCD:
    baseURL = 'https://us-central1-upnext-8f097.cloudfunctions.net/app'


def safe_exit(signum, frame):
    exit(1)

def displayPlaybackInfo(conn2):
    # calls functions that start with display
    
        #piCode = conn2.recv()
        #displayLoginInfo(lcd, piCode)
    storedString = ''
        
    while True:
        #if not conn2.poll():
        #    return
        
        data = conn2.recv()
        print(data)

        if not HAS_LCD:
            continue
        

        if data.get("piCode"):
            p1 = multiprocessing.Process(
                target=displayLoginInfo,
                args=(lcd, data["piCode"],))
            p1.start()
            data = conn2.recv()
            p1.kill()
            p1.join()
            #continue

        if storedString == data.get("string"):
            continue            
        print("printing to screen")
        storedString = data.get("string")
        p1 = multiprocessing.Process(
            target=displayString,
            args=(lcd, 16,
            "",data.get("string"),
            "",data.get("string2"),))

        p1.start()
        #time.sleep(1000)
        data = conn2.poll(None)
        p1.kill()
        p1.join()

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
        controller = LCDController()
        """lcdProcess = multiprocessing.Process(
            target=displayPlaybackInfo,
            args=(conn2,))
        lcdProcess.start()"""
        controller.displayLoginInfo(piCode)
        while False:
            time.sleep(10)


        #conn1.send({"piCode": piCode})
        headers = getHeaders(piCode)
        previousString = ""

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
                    #conn1.send({"piCode": piCode})
                    controller.displayLoginInfo(piCode)
                    headers = getHeaders(piCode)

            try:
                nowPlaying = nowPlaying["item"]["name"]
                nextUp = queue["queue"][0]["name"]
                
                #only update if available and changed
                if nowPlaying + nextUp != previousString:
                    print(nextUp, ' ', nowPlaying)
                    previousString = nowPlaying + nextUp
                    controller.setString(0, "Now:", nowPlaying)
                    controller.setString(1, "Next:", nextUp)
                    controller.updateLCD()
            except:
                print("nothing is playing at the moment")
            time.sleep(5)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('Exception has occured: ', e)
        logger.exception(e)
