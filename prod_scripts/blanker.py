#!/usr/bin/python3
import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
import time
import threading
import os
import stat

def bus_call(bus, msg, *args):
	if msg.type == Gst.MessageType.EOS:
		print("End-of-stream")
		loop.quit()
		return
	elif msg.type == Gst.MessageType.ERROR:
		print("GST ERROR", msg.parse_error())
		loop.quit()
		return
	return True

def quit():
	pipeline.send_event(Gst.Event.new_eos())

def set_text(t):
	text = pipeline.get_by_name ("text")
	text.set_property("text", t)

def control():
	FIFO="/tmp/blankerfifo"
	if os.path.exists(FIFO):
		if not stat.S_ISFIFO(os.stat(FIFO).st_mode):
			os.remove(FIFO)
			os.mkfifo(FIFO)
	else:
		os.mkfifo(FIFO)

	while True:
		with open(FIFO) as fifo:
			line=fifo.read().strip()
			print("Got: ", line)
			if "=" not in line:
				print("Invalid line.")
				continue
			key = line.split("=")[0]
			val = line.split("=")[1]

			if key == "text":
				print("Got text, value %s" % val)
				set_text(val)

			
if __name__ == "__main__":
	if 'LD_LIBRARY_PATH' not in os.environ:
		os.environ['LD_LIBRARY_PATH'] = '/usr/local/lib'
		os.execv(sys.argv[0], sys.argv)
	# initialization
	Gst.init(None)

	p = '''multifilesrc location="/var/voctomix/prod_scripts/blanker.h264" loop=1 !
		h264parse ! avdec_h264 !
		videoconvert ! videorate !
		video/x-raw,format=I420,width={WIDTH},height={HEIGHT},framerate={FRAMERATE}/1,pixel-aspect-ratio=1/1 !
		textoverlay text="La transmisión iniciará en 3 minutos" valignment=position ypos=0.6 font-desc="sans-serif 14" name=text !
		matroskamux !
		tcpclientsink host=localhost port=17000'''.format(WIDTH=1280, HEIGHT=720, FRAMERATE=25)
	print(p)
	pipeline = Gst.parse_launch (p)
	if pipeline == None:
		print ("Failed to create pipeline")
		sys.exit(0)


	# run
	pipeline.set_state(Gst.State.PLAYING)
	t = threading.Thread(target=control, daemon=True)
	t.start()
	while True:
		time.sleep(10000)

	# cleanup
	pipeline.set_state(Gst.State.NULL)

