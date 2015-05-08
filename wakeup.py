#!/usr/bin/python

import oled
from sunrise import *
from threading import *
import time
import sqlite3
import sys

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
        db.commit()
        c=db.cursor()
        t=time.localtime()
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
        bus=oled.init()

        db = sqlite3.connect('wakeup.db')
        m = 60
        while True:
                if(m!=time.strftime("%M",time.localtime())):
                        updateScreen(db,bus)
                        m=time.strftime("%M",time.localtime())
                        if(timerHit(db)):
                                sunrise_t_stop=Event()
                                sunrise_t=Thread(target=sunrise,args=(sunrise_t_stop,))
                                sunrise_t.daemon=True
                                sunrise_t.start()
                time.sleep(1.5)




if __name__ == '__main__':
        try:
                main()
        except KeyboardInterrupt:
                GPIO.cleanup()
