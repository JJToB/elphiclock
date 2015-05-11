#!/usr/bin/python
import time
import neopixel

# LED strip configuration:
LED_COUNT   = 60      # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)

global mode, mode_step, modes, mode_position, strip, fb
mode=0;
mode_step=1
mode_position=0
modes = { 0: mode_none,
          1: mode_off,
          2: mode_sunrise,
          3: mode_sunset,
          4: mode_mood }


# Basic functions

def initStrip():
        strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)    # Create strip
        fb=range(strip.numPixels())                                                                 # Create Framebuffer
        for j in range(strip.numPixels()):                                                          # Loop through FB
                fb[j]=[0,0,0]                                                                       # Set to black
        strip.begin()                                                                               # Start communication
        drawFB(strip,fb)                                                                            # Send FB to strip

def drawFB(strip,fb):
        for j in range(strip.numPixels()):                                                          # Loop through stripe
                strip.setPixelColor(j,Color(fb[j][0],fb[j][1],fb[j][2]))                            # Send pixel
        strip.show()                                                                                # Activate leds
                
def refresh_LEDs():
        global modes, mode, fb, strip
        if(modes[mode]()):                                                                          # Execute mode-function
                drawFB(strip,fb)                                                                    # Send FB to strip

# Color functions

def decCol(fb,i,c):
        if(fb[i][c]>0):
                fb[i][c]=(fb[i][c]-1)

def incCol(fb,i,c):
        if(fb[i][c]<255):
                fb[i][c]=(fb[i][c]+1)

def fadeFromMiddle(level,c,direction=0):                                                            # Fade color c to level
	      global strip,fb                                                                             # Direction: 0:both, 1:up, 2:down
        for i in reversed(range(strip.numPixels()/2)):
                 if(fb[i][c]!=level):                                                               # If not desired color
                        if(fb[i][c]<level and direction != 2):                                      # If color is < level and not dec-only
                               incCol(fb,i,c)                                                       # Increase color
                        if(fb[i][c]>level and direction != 1):                                      # If color is > level and not inc-only
                               decCol(fb,i,c)                                                       # Decrease color
                        fb[(strip.numPixels()-i-1)]=fb[i]                                           # Copy to other half of strip
                        return(False)                                                               # Quit round
        return(True)                                                                                # Mark complete

def fadeAll(level,c,direction=0):                                                                   # Fade color c to level
	      global strip,fb                                                                             # Direction: 0:both, 1:up, 2:down
	      complete=True
        for i in range(strip.numPixels()/2):
                 if(fb[i][c]!=level):                                                               # If not desired color
                        if(fb[i][c]<level and direction != 2):                                      # If color is < level and not dec-only
                               incCol(fb,i,c)                                                       # Increase color
                        if(fb[i][c]>level and direction != 1):                                      # If color is > level and not inc-only
                               decCol(fb,i,c)                                                       # Decrease color
                        fb[(strip.numPixels()-i-1)]=fb[i]                                           # Copy to other half of strip
                 if(fb[i][c]!=level):                                                               # Check again if complete
                        complete=False                                                              # Mark incomplete
        return(complete)


# Modes

def mode_sunrise():
        global strip, mode, fb, mode_step, mode_position
        if(mode_step == 1):
                if(fadeFromMiddle(5,2)):                                                            # Make light blue backlight
                        mode_step=(mode_step+1)                                                     # Continue with next step
                        mode_position=0                                                             # Reset position for next step
        elif(mode_step == 2):
                fadeFromMiddle(20,0,1)                                                              # Turn to red
                if(mode_position > ((strip.numPixels()/12)*20)                                      # When at 1/6 of the half stripe
                       fadeFromMiddle(40,0,1)                                                       # Start second wave to red
                       fadeFromMiddle(50,1,1)                                                       # Start fading to yellow
                       if(mode_position > ((strip.numPixels()/12)*40)                               # When at 1/3 of the half stripe
                              if(fadeFromMiddle(60,0,1) and                                         # Start third wave to red
                                 fadeFromMiddle(60,1,1) ):                                          # Start second wave to yellow
                                     mode_step=(mode_step+1)                                        # Go to next step
                mode_position=(mode_position+1)
        elif(mode_step == 3):
                if( fadeFromMiddle(80,0) and                                                        # Fade all to white
                    fadeFromMiddle(80,1) and                                                        # Fade all to white
                    fadeFromMiddle(80,2) ):                                                         # Fade all to white
                    mode_step=(mode_step+1)                                                         # Go to next step
        elif(mode_step == 4):
                if( fadeFromMiddle(255,0) and                                                       # Fade all to bright white
                    fadeFromMiddle(255,1) and                                                       # Fade all to bright white
                    fadeFromMiddle(255,2) ):                                                        # Fade all to bright white
                    mode_step=(mode_step+1)                                                         # Go to next step
        else:
                mode=0                                                                              # Set mode to 0
                mode_step=1                                                                         # Reset step

def mode_off():
        global mode
        if(fadeAll(0,0) and                                                                         # Turn all LEDs off
           fadeAll(0,1) and
           fadeAll(0,2)):
                mode=0                                                                              # Set mode to 0

def mode_mood():
        global mode
        if(fadeAll(60,0) and                                                                        # Turn all LEDs to mood-color
           fadeAll(0,1) and
           fadeAll(60,2)):
                mode=0                                                                              # Set mode to 0

def mode_none():
        return(False)                                                                               # No need to update stripe
