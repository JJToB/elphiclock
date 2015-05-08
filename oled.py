import smbus
import time

BUS_ID = 1
BUS_ADDR = 0x27

def dayName(dow):
        days = {
                0: "Sunday",
                1: "Monday",
                2: "Tuesday",
                3: "Wednesday",
                4: "Thursday",
                5: "Friday",
                6: "Saturday"
        }
        return(days[dow])


def init():
   bus=smbus.SMBus(BUS_ID)
   clear(bus)
   sendWord(bus,"CS0")            # Disable Cursor
   return(bus)

def sendWord(bus, val):
   for character in str(val):
      bus.write_byte(BUS_ADDR , ord(character))

def sendValue(bus,val):
   bus.write_byte(BUS_ADDR, val)

def clear(bus):
   sendWord(bus,"CL")

def writeText(bus, text):
   sendWord(bus,"TT"+text+"\n")

def drawRect(bus,x1,y1,x2,y2):
   sendWord(bus,"DR")
   sendValue(bus,x1)
   sendValue(bus,y1)
   sendValue(bus,x2)
   sendValue(bus,y2)

def setFont(bus,font):
   sendWord(bus,"SF")
   sendValue(bus,font)

def setColor(bus,color):
   sendWord(bus,"SC")
   sendValue(bus,color)

def grey(bus,bright):
        if(bright==0):
                setColor(bus,0)
        else:
                if(bright==1):
                        setColor(bus,182)
                else:
                        setColor(bus,218)

def blue(bus,bright):
   setColor(bus,bright+5)

def green(bus,bright):
   if(bright==0):
        bright=1
   bright=((bright*12)+8)
   if(bright>28):
      bright=28
   setColor(bus,bright)

def red(bus,bright):
   bright=((bright*64)+64)
   if(bright>224):
      bright=224
   setColor(bus,bright)

def setPos(bus,x,y):
   sendWord(bus,"TP")
   sendValue(bus,x)
   sendValue(bus,y)

def screenTimes(bus,next):
        if (9 <= int(time.strftime("%H",time.localtime())) < 22):
                bright=2
        else:
                bright=0
        if(next):
                print next
                row=0
                for timer in next:
                        print timer
                        setFont(bus,0)
                        if(timer[3]):
                                green(bus,bright)
                        else:
                                red(bus,bright)
                        setPos(bus,0,row)
                        writeText(bus,"%09s, %02u:%02u" % (dayName(timer[2]), timer[0], timer[1]))
                        row=(row+1)
        setFont(bus,120)
        blue(bus,bright)
        setPos(bus,13,3)
        writeText(bus,time.strftime("%H:%M", time.localtime()))
