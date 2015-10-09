import smbus
import oled_image2
import time

BUS_ID = 1
BUS_ADDR = 0x27
imgSent=False

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
   global imgSent
   imgSent=False
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

def setColor(bus,r,g,b):
   sendWord(bus,"ESC")
   sendValue(bus,r)
   sendValue(bus,g)
   sendValue(bus,b)

def grey(bus,bright):
   setColor(bus,(bright*100+15),(bright*100+15),(bright*100+15))

def blue(bus,bright):
   setColor(bus,0,0,(bright*120+15))

def green(bus,bright):
   setColor(bus,0,(bright*118+19),0)

def red(bus,bright):
   setColor(bus,(bright*120+15),0,0)

def black(bus):
   setColor(bus,0,0,0)

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
		clear(bus)
                row=1
                for timer in next:
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

def screenRunning(bus):
	global imgSent
	sendWord(bus,"DM^")
	setFont(bus,120)
	black(bus)
	if(imgSent):
		setPos(bus,13,3)
		#writeText(bus,time.strftime("%H:%M", (int(time.localtime())-60)))
	else:
		imgSent=True
		drawImage(bus,0,0,160,128,oled_image2.sun())
	setPos(bus,13,3)

def drawImage(bus,x,y,w,h,data):
	#sendWord(bus,"SSS")
	#print((len(data)+9))
	#sendValue(bus,(len(data)+9))
	sendWord(bus,"EDIM1")
	sendValue(bus,x)
	sendValue(bus,y)
	sendValue(bus,w)
	sendValue(bus,h)
	for b in data:
		sendValue(bus,b)
