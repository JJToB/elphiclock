#!/usr/bin/python

import oled
from threading import *
import time
import sqlite3
import sys
import stripe
import RPi.GPIO as GPIO                                                         # GPIO for buttons

global config,speeds,btncnt
btncnt=0

speeds = { 0: 2,
   1: 1,
   2: 0.5,
   3: 0.2,
   4: 0.1,
   5: 0.05,
   6: 0.02,
   7: 0.01 }

config = { 'start_before': 8,                                                   # Minutes to stard before Time
   'speed': 6 }                                                         # Speed for Animations


def getNextTimer(db):
	c=db.cursor()
	t=time.localtime()
	h=time.strftime("%H",t)
	m=time.strftime("%M",t)
	d=time.strftime("%e",t)
	w=time.strftime("%w",t)
	c.execute('SELECT h,m,w,active FROM times WHERE ( \
			w='+w+' \
			AND ( \
				h>'+h+' \
				OR ( h='+h+' AND m>'+m+' ) \
			) \
			AND last!='+d+' \
		) OR ( \
			w='+str(int(w)+1)+' \
			AND ( \
				h<'+h+' \
				OR ( h='+h+' AND m<'+m+' ) \
			) \
		) \
		ORDER BY w,h,m;')
	print ('SELECT h,m,active FROM times WHERE (w='+w+'     AND (h>'+h+' OR (h='+h+' AND m>'+m+' )) AND last!='+d+') OR (w='+str(int(w)+1)+' AND (h<'+h+' OR (h='+h+' AND m<'+m+'))) ORDER BY w,h,m;')
	data=c.fetchall()
	return data


def timerHit(db):
	global config,speeds
	db.commit()
	c=db.cursor()
	t=time.localtime(time.mktime(time.localtime())+(config['start_before']*60))
	h=time.strftime("%H",t)
	m=time.strftime("%M",t)
	d=time.strftime("%e",t)
	w=time.strftime("%w",t)
	c.execute('SELECT * FROM times WHERE h='+h+' AND m='+m+' AND w='+w+' AND active=1 AND last!='+d+';')
	data=c.fetchone()
	if(data):
		c.execute('UPDATE times SET last='+d+' WHERE h='+h+' AND m='+m+' AND w='+w+' AND active=1;')
		db.commit()
		print('UPDATE times SET last='+d+' WHERE h='+h+' AND m='+m+' AND w='+w+' AND active=1;')
		print "Executing"
		return True
	return False

def updateScreen(db,bus):
	next=getNextTimer(db)
	oled.screenTimes(bus,next)

def main():
	global config,speeds,btncnt
	bus=oled.init()
	stripe.initStrip()
	GPIO.setmode(GPIO.BCM)                                                          # Setup GPIO
	GPIO.setup(27,GPIO.IN, pull_up_down=GPIO.PUD_UP)                                # Initialize GPIO27


	db = sqlite3.connect('wakeup.db')
	m = 60											# Setup out of range to force refresh on startup
	while True:
		if(m!=time.strftime("%M",time.localtime())):
			print(str(time.strftime("%M",time.localtime())))
			if(stripe.running()):
				oled.screenRunning(bus)
			else:
				updateScreen(db,bus)
			m=time.strftime("%M",time.localtime())
			if(timerHit(db)):
				stripe.start_sunrise()
               	time.sleep(speeds[config['speed']])
		stripe.refresh_LEDs()
		if GPIO.input(27):                                                      # Check if button released
			if btncnt > 2:                                                  # and was pressed before
				if(stripe.running()):
					print("Stopping")
                               		stripe.stop_all()                               # TurnOff
				else:
					print("Mood")
					stripe.start_mood()
               		btncnt = 0                                                      # Reset counter
		else:                                                                   # if pressed
			print("PRESSED")
			btncnt += 1                                                     # Increment counter
			if btncnt > 1000:                                               # Prevent overrun
				btncnt=500





if __name__ == '__main__':
        try:
                main()
        except KeyboardInterrupt:
                GPIO.cleanup()
