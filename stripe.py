#!/usr/bin/python
import neopixel										# For ws2812b control

# LED strip configuration:
L_CNT = 6										# Number of LED pixels.
L_PIN = 18										# GPIO pin connected to the pixels (must support PWM!).

# Variable declaration

global mode, mode_step, modes, mode_position, strip, fb
mode=0;
mode_delay=0;
mode_step=1
mode_position=0

# Basic functions

def initStrip():
	global strip,fb
	strip = neopixel.Adafruit_NeoPixel(L_CNT, L_PIN, 800000, 5, False)		# Create strip
	fb=range(strip.numPixels())							# Create Framebuffer
	for j in range(strip.numPixels()):						# Loop through FB
		fb[j]=[0,0,0]								# Set to black
	strip.begin()									# Start communication
	drawFB(strip,fb)								# Send FB to strip

def drawFB(strip,fb):
	for j in range(strip.numPixels()):						# Loop through stripe
		strip.setPixelColor(j,neopixel.Color(fb[j][0],fb[j][1],fb[j][2]))	# Send pixel
	strip.show()									# Activate leds
                
def refresh_LEDs():
	global mode, fb, strip
	if(mode==1):									# Execute mode functions
		mode_off()
	elif(mode==2):
		mode_sunrise()
	elif(mode==3):
		mode_sunset()
	elif(mode==4):
		mode_mood()
	if(mode>=0):
		drawFB(strip,fb)							# Send FB to strip

def running():
	global mode, fb, strip
	return(mode>=2)									# True if mode >= 2

# Color functions

def decCol(fb,i,c):									# lower one color
	if(fb[i][c]>0):									# if not already 0x00
		fb[i][c]=(fb[i][c]-1)							# decrement by one

def incCol(fb,i,c):									# higher one color
	if(fb[i][c]<255):								# if not already 0xFF
		fb[i][c]=(fb[i][c]+1)							# increment by one

def fadeFromMiddle(level,c,direction=0):						# Fade color c to level pixel by pixel
	global strip,fb 								# Direction: 0:both, 1:up, 2:down
	for i in reversed(range(strip.numPixels()/2)):					# For each pixel in lower half strip
		if(fb[i][c]!=level):							# If not desired color
			if(fb[i][c]<level and direction != 2):				# If color is < level and not dec-only
				incCol(fb,i,c)						# Increase color
			if(fb[i][c]>level and direction != 1):				# If color is > level and not inc-only
				decCol(fb,i,c)						# Decrease color
			fb[(strip.numPixels()-i-1)]=fb[i]				# Copy to other half of strip
			return(False)							# Quit round
	return(True)									# Mark complete

def fadeAll(level,c,direction=0):							# Fade color c to level all even
	global strip,fb									# Direction: 0:both, 1:up, 2:down
	complete=True
	for i in range(strip.numPixels()/2):
		if(fb[i][c]!=level):							# If not desired color
			if(fb[i][c]<level and direction != 2):				# If color is < level and not dec-only
				incCol(fb,i,c)						# Increase color
			if(fb[i][c]>level and direction != 1):				# If color is > level and not inc-only
				decCol(fb,i,c)						# Decrease color
			fb[(strip.numPixels()-i-1)]=fb[i]				# Copy to other half of strip
		if(fb[i][c]!=level):							# Check again if complete
			complete=False							# Mark incomplete
	return(complete)


# Modes

def mode_sunrise():
	global strip, mode, fb, mode_step, mode_position, mode_delay
	if(mode_delay>10):								# If delay hit
		mode_delay=0								# reset delay
		if(mode_step == 1):
			if(fadeFromMiddle(5,2)):					# Make light blue backlight
				mode_step=(mode_step+1)					# Continue with next step
				mode_position=0						# Reset position for next step
		elif(mode_step == 2):
			fadeFromMiddle(20,0,1)						# Turn to red
			if(mode_position > ((strip.numPixels()/12)*20)):		# When at 1/6 of the half stripe
				fadeFromMiddle(40,0,1)					# Start second wave to red
				fadeFromMiddle(50,1,1)					# Start fading to yellow
				if(mode_position > ((strip.numPixels()/12)*40)):	# When at 1/3 of the half stripe
					if(fadeFromMiddle(60,0,1) and			# Start third wave to red
						fadeFromMiddle(60,1,1) ):		# Start second wave to yellow
						mode_step=(mode_step+1)			# Go to next step
			mode_position=(mode_position+1)
		elif(mode_step == 3):
			if( fadeFromMiddle(80,0) and					# Fade all to white
			fadeFromMiddle(80,1) and					# Fade all to white
			fadeFromMiddle(80,2) ):						# Fade all to white
				mode_step=(mode_step+1)					# Go to next step
	                  	 
		elif(mode_step == 4):
			if( fadeFromMiddle(255,0) and					# Fade all to bright white
			fadeFromMiddle(255,1) and					# Fade all to bright white
			fadeFromMiddle(255,2) ):					# Fade all to bright white
				mode_step=(mode_step+1)					# Go to next step
		else:
			print("Done")
	else:
		mode_delay=(mode_delay+1)						# increment delay counter

def mode_sunset():
	global mode									# ToDo: Just a cheap copy of mood
	if(fadeAll(80,0) and								# set red to sunset-level
	 fadeAll(48,1)):								# set red to sunset-level
		fadeAll(1,2)								# set blue to sunset-level

def mode_off():
	global mode
	if(fadeAll(0,0) and								# remove red
	 fadeAll(0,1) and								# remove green
	 fadeAll(0,2)):									# remove blue
		mode=0									# Set mode to 0

def mode_mood():
	global mode
	if(fadeAll(60,0) and								# set red to mood-level
	 fadeAll(0,1)):									# remove green
		fadeAll(60,2)								# set blue to mood-level

def reset_mode():
	global mode_step,mode_position
	mode_step=1									# set to first step
	mode_position=0									# reset mode position

def start_sunrise():
	global mode
	reset_mode()									# reset mode
	mode=2										# set mode to sunrise-mode

def start_sunset():
	global mode
	reset_mode()									# reset mode
	mode=3										# set mode to sunset-mode

def start_mood():
	global mode
	reset_mode()									# reset mode
	mode=4										# set mode to mood-mode

def stop_all():
	global mode
	reset_mode()									# reset mode
	mode=1										# set mode to off-mode
