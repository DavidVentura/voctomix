#!/usr/bin/env python3
import datetime
import sys
import time

def minutes(t):
    hour = int(t.split(":")[0])
    minute = int(t.split(":")[1])

    now     = datetime.datetime.now()
    target  = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    delta = target-now
    if delta.days < 0:
        return 1 #1 minute if we have gone over the top

    minutes_left = int(delta.seconds/60)
    minutes_left = max(minutes_left, 1)
    return minutes_left

if __name__ == "__main__":

    if len(sys.argv) == 2:
        fifo = open("/tmp/blankerfifo", "w")
        fifo.write("text=%s\n" % sys.argv[1])
        fifo.flush()
        fifo.close()
        exit(0)

    if len(sys.argv) != 3:
        print("usage: %s HH:MM Text" % sys.argv[0])
        print("Text must contain exactly one '%s'")
        sys.exit(1)

    t = sys.argv[1]
    if t.count(":") != 1:
        print("Time format: HH:MM")
        sys.exit(1)

    text = sys.argv[2]
    if text.count("%s") != 1:
        print("Text must contain exactly one '%s'")
        sys.exit(1)

    while True:
        try:
            m = max(minutes(t), 1)
        except Exception as e:
            print(e)
            sys.exit(1)

        fifo = open("/tmp/blankerfifo", "w")
        outtext = (text % str(m))
        if m == 1:
            outtext = outtext.replace("minutos", "minuto")
        fifo.write("text=%s\n" % outtext)
        print(outtext)
        fifo.close()
        if m == 1:
            break
        time.sleep(30)
