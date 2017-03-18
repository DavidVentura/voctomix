#!/usr/bin/env python3
import os
import queue
import shlex
import sys
import time
import threading
from subprocess import PIPE, Popen

# This "smart" pipe dies if either its stdin dies or its child
# (passed as argument)produces something on stderr.
# This is useful because ffmpeg -xerror doesn't always exit on error.
# That is a known bug and affecting me.

q = queue.Queue()
working = True


def debug(s):
    print("[DEBUG] ", s)


def millis():
    return int(round(time.time() * 1000))


def die():
    global working
    working = False
    debug("Bye")
    sys.exit(1)


def read_stdin():
    stdin = os.fdopen(sys.stdin.fileno(), 'rb')
    while working:
        try:
            data = stdin.read(4096)
        except:
            die()
        if not data:
            print("no data")
            die()
        q.put(data)


def setup_child(command):
    proc = shlex.split(command)
    return Popen(proc, stdin=PIPE, stderr=PIPE, bufsize=1)


def watch_stderr(child):
    while working:
        data = child.stderr.readline()
        if data != b"":
            print(data)
            print("suiciding")
            # child.terminate(timeout=1)
            die()


def write_tochild(child):
    while working:
        try:
            data = q.get()
            child.stdin.write(data)
            # child.stdin.flush()
        except Exception as e:
            print("except writing to child")
            print(e)
            die()


def main(command):
    child = setup_child(command)

    debug("Child started")

    stdin = threading.Thread(target=read_stdin, daemon=True)
    stdout = threading.Thread(target=write_tochild, args=(child,), daemon=True)
    stderr = threading.Thread(target=watch_stderr, args=(child,), daemon=True)

    stdin.start()
    stdout.start()
    stderr.start()

    debug("Threads started")

    while working:
        time.sleep(0.2)

    debug("Exiting main, not working anymore")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage %s quoted_command" % sys.argv[0])
        sys.exit(1)
    main(sys.argv[1])
