#!/usr/bin/python
import time

from neopixel import *


# LED strip configuration:
LED_COUNT   = 60      # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)

def fadeToBlue(strip, fb,wait_ms,sunrise_t_stop):
        for j in range(4):
                for i in reversed(range(strip.numPixels()/2)):
                        incCol(fb,i,2)
                        fb[(strip.numPixels()-i-1)]=fb[i]
                        if(sunrise_t_stop.is_set()): return()
                        drawFB(strip,fb)
                        time.sleep(wait_ms/1000.0)

def pulseWhite(strip, fb,wait_ms,sunrise_t_stop):
        for j in range(511):
                for i in range(strip.numPixels()):
                        if(j>=255):
                                decCol(fb,i,0)
                                decCol(fb,i,1)
                                decCol(fb,i,2)
                        else:
                                incCol(fb,i,0)
                                incCol(fb,i,0)
                                incCol(fb,i,1)
                if(sunrise_t_stop.is_set()): return()
                drawFB(strip,fb)
                time.sleep(wait_ms/1000.0)

def blinkWhite(strip, fb,wait_ms,times,sunrise_t_stop):
        for n in range(times):
                for i in range(strip.numPixels()):
                        if(n % 2 == 0):
                                fb[i]=[0,0,0]
                        else:
                                fb[i]=[255,255,255]
                if(sunrise_t_stop.is_set()): return()
                drawFB(strip,fb)
                time.sleep(wait_ms/1000.0)

def fadeToWhite(strip, fb,wait_ms,sunrise_t_stop):
        for j in range(255):
                for i in reversed(range(strip.numPixels()/2)):
                        incCol(fb,i,0)
                        incCol(fb,i,1)
                        incCol(fb,i,2)
                        fb[(strip.numPixels()-i-1)]=fb[i]
                        if(sunrise_t_stop.is_set()): return()
                        drawFB(strip,fb)
                        time.sleep(wait_ms/1000.0)

def decCol(fb,i,c):
        if(fb[i][c]>0):
                fb[i][c]=(fb[i][c]-1)

def incCol(fb,i,c):
        if(fb[i][c]<255):
                fb[i][c]=(fb[i][c]+1)

def fadeToRed(strip, fb,wait_ms,sunrise_t_stop):
        g=0
        for r in range(1,44):
                if(r>12):
                        g=(g+1)
                for k in range(r):
                        for i in range(strip.numPixels()/2):
                                if(((strip.numPixels()/2)-k)<=i):
                                        incCol(fb,i,0)
                                        if(k<=g):
                                                incCol(fb,i,1)
                                fb[(strip.numPixels()-i-1)]=fb[i]
                        if(sunrise_t_stop.is_set()): return()
                        drawFB(strip,fb)
                        time.sleep(wait_ms/1000.0)

def drawFB(strip,fb):
        for j in range(strip.numPixels()):
                strip.setPixelColor(j,Color(fb[j][0],fb[j][1],fb[j][2]))
        strip.show()

def createFB(strip):
        fb=range(strip.numPixels())
        for j in range(strip.numPixels()):
                fb[j]=[0,0,0]
        return(fb)

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT)
fb=createFB(strip)
strip.begin()
drawFB(strip,fb)

def sunrise(sunrise_t_stop):
        fadeToBlue(strip,fb,300,sunrise_t_stop)
        fadeToRed(strip,fb,300,sunrise_t_stop)
        fadeToWhite(strip,fb,30,sunrise_t_stop)
        for i in [50,40,30,20,10,5,2,1,1,1]:
                pulseWhite(strip,fb,i,sunrise_t_stop)
        blinkWhite(strip,fb,100,100,sunrise_t_stop)

