from signal import signal, SIGTERM, SIGHUP, pause
from RPLCD.i2c import CharLCD
import time
import multiprocessing


def safe_exit(signum, frame):
    exit(1)
    
framebuffer = [
    "",
    '',
]

def write_to_lcd(lcd, string, num_cols):
    """Write the framebuffer out to the specified LCD."""
    lcd.home()
    #lcd.cursor_pos = (row, 0)
    print(string)
    lcd.write_string(string)

def displayString( lcd, num_cols, staticText, string, staticText2="", string2="", delay=0.5):
    
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
        

class loop_string(multiprocessing.Process):
    framebuffer = ["",""]

    def __init__(self, string, string2, lcd, num_cols, delay=0.5):
        super(loop_string, self).__init__()
        self.string = string
        self.string2 = string2
        self.lcd = lcd
        self.num_cols = num_cols
        self.delay = delay
                 
    def run(self):
        
        padding = ' ' * self.num_cols
        s = padding + self.string + padding
        
        padding2 = ' ' * self.num_cols
        s2 = padding2 + self.string2 + padding2
        longest = max(len(s), len(s2))
        i = self.num_cols
        k = self.num_cols
        while True:
            #for i in range(len(s) - self.num_cols + 1):
            
            framebuffer[0] = s[i:i+self.num_cols]#.ljust(self.num_cols)
            framebuffer[1] = s2[k:k+self.num_cols]#.ljust(self.num_cols)
            joinedString = framebuffer[0] + "\r\n" + framebuffer[1]
            write_to_lcd(self.lcd, joinedString, self.num_cols)
            i+=1
            k+=1
            if k == len(s2) - self.num_cols:
                k = 0 #self.num_cols
            if i == len(s) - self.num_cols:
                i = 0 #self.num_cols
            time.sleep(self.delay)
        
try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)
    lcd = CharLCD('PCF8574', 0x27)
    lcd.clear()
    
    long_string = 'Feel The Volume - JAUZ'
    long_string2 = 'The Calling - Tchami'
    
    displayString(lcd, 16, "Now Playing:", long_string, "Next Up:", long_string2)


except KeyboardInterrupt:
    pass
finally:
    lcd.clear()

