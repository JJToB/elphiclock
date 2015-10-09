#!/usr/bin/python

import oled										# for OLED display
import time										# for delay function
import sqlite3										# for database
import stripe										# for wS2812b Stripe functions
import RPi.GPIO as GPIO									# GPIO for buttons

global config,speeds,btncnt
btncnt=0

config = { 'start_before': 8 }								# Minutes to stard before Time


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
	data=c.fetchall()								# Get timers for next 24 hours
	return data


def timerHit(db):
	global config,speeds
	db.commit()
	c=db.cursor()
	t=time.localtime(time.mktime(time.localtime())+(config['start_before']*60))	# Consider prestart time
	h=time.strftime("%H",t)
	m=time.strftime("%M",t)
	d=time.strftime("%e",t)
	w=time.strftime("%w",t)
	c.execute('SELECT * FROM times WHERE h='+h+' AND m='+m+' AND w='+w+' AND active=1 AND last!='+d+';')
	data=c.fetchone()								# Select timer for now from DB
	if(data):
		c.execute('UPDATE times SET last='+d+' WHERE h='+h+' AND m='+m+' AND w='+w+' AND active=1;')
		db.commit()								# Update current timer
		print "Executing"							# ToDo: Remove debug
		return True
	return False

def main():										# Main function
	global config,speeds,btncnt
	bus=oled.init()									# Initialize Display
	stripe.initStrip()								# Initialize LED Stripe
	GPIO.setmode(GPIO.BCM)								# Setup GPIO
	GPIO.setup(27,GPIO.IN, pull_up_down=GPIO.PUD_UP)				# Initialize GPIO27


	db = sqlite3.connect('wakeup.db')
	m = 60										# Setup out of range to force refresh on startup
	while True:
		if(m!=time.strftime("%M",time.localtime())):				# when minute changed
			print(str(time.strftime("%H:%M",time.localtime())))		# ToDo: Remove debug
			if(stripe.running()):						# If light is on
				oled.screenRunning(bus)					# Show running screen
			else:
				oled.screenTimes(bus,getNextTimer(db))			# Show Timeing screen
			m=time.strftime("%M",time.localtime())				# store actual minute
			if(timerHit(db)):						# If need to start wakeup
				stripe.start_sunrise()					# Start sunrise-mode
               	time.sleep(0.02)							# Small delay
		stripe.refresh_LEDs()							# continue LED animation and efresh stripes
		if GPIO.input(27):							# Check if button released...
			if btncnt > 2:							# ...and was pressed before ToDo: Long press action
				if(stripe.running()):
                               		stripe.stop_all()				# TurnOff
				else:
					stripe.start_mood()				# Start mood
               		btncnt = 0							# Reset counter
		else:									# if pressed
			btncnt += 1							# Increment counter
			if btncnt > 1000:						# Prevent overrun
				btncnt=500





if __name__ == '__main__':
        try:
                main()
        except KeyboardInterrupt:
                GPIO.cleanup()
