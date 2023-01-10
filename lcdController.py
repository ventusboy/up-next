from RPLCD.i2c import CharLCD
from dotenv import load_dotenv, dotenv_values
import time, math, asyncio
import multiprocessing

config = dotenv_values(".env.local")
HAS_LCD = False
if 'HAS_LCD' in config:
    HAS_LCD = config["HAS_LCD"]


class LCDController:

    def __init__(self):
        lcd = CharLCD('PCF8574', 0x27)
        lcd.clear()

        conn1, conn2 = multiprocessing.Pipe()
        self.lcd = lcd
        self.num_cols = 16
        self.conn1 = conn1
        self.strings = ["", ""]
        self.staticStrings = ["", ""]
        #self.displayLoginInfo('mikal')
        self.p1 = multiprocessing.Process(
            target=self.loopString,
            args=(conn2,)
            )
        self.p1.start()

    
    def write_to_lcd(self, string):
        """Write the framebuffer out to the specified LCD."""
        print(string)
        self.lcd.home()
        self.lcd.write_string(string)
    
    def setString(self, row, staticText="", string=""):
        if row > 1:
            return
        if len(staticText) > self.num_cols:
            string = (staticText.rstrip() + ' ' + string).strip()
            staticText = ""
        if len(staticText) + len(string) < self.num_cols:
            staticText = (staticText.rstrip() + ' ' + string).strip()
            string = ""

        self.strings[row] = string
        self.staticStrings[row] = staticText
        
    
    def loopString(self, conn2, delay=0.5):

        framebuffer = ["", ""]
        num_cols = self.num_cols

        padding = ' ' * num_cols
        strings = ["", ""]
        staticStrings = ["", ""]

        s = padding * 2
        s2 = padding * 2

        i = num_cols
        k = num_cols
        while True:
            if conn2.poll():
                data = conn2.recv()
                strings = data["strings"]
                staticStrings = data["staticStrings"]
                s = padding + strings[0] + padding
                s2 = padding + strings[1] + padding
                i = math.floor(num_cols / 2) # start the string in the middle
                k = math.floor(num_cols / 2)

            framebuffer[0] = staticStrings[0] + s[i:i+num_cols - len(staticStrings[0])]
            framebuffer[1] = staticStrings[1] + s2[k:k+num_cols - len(staticStrings[1])]
            joinedString = framebuffer[0] + "\r\n" + framebuffer[1]
            self.write_to_lcd(joinedString)

            if len(s) > 2 * num_cols:
                i += 1
            if len(s2) > 2 * num_cols:
                k += 1

            if i == len(s) - num_cols:  # + len(staticText):
                i = 0 + len(staticStrings[0])
            if k == len(s2) - num_cols:  # + len(staticText2):
                k = 0 + len(staticStrings[1])

            time.sleep(delay)
    
    def displayLoginInfo(self, piCode):
        self.setString(0, "Your code: " + piCode)
        self.setString(1, "At upnext.mikalyoung.com")
        self.updateLCD()
        
    def updateLCD(self):
        self.conn1.send({
            "strings": self.strings,
            "staticStrings": self.staticStrings
        })



