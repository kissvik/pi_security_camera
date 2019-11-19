
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import warnings
import datetime
import imutils
import json
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
	help="A konfigurációs JSON file elérési útvonala")
args = vars(ap.parse_args())

conf = json.load(open(args["conf"]))


picamera = PiCamera()
picamera.resolution = tuple(conf["resolution"])
picamera.framerate = conf["fps"]
rawCapture = PiRGBArray(picamera, size=tuple(conf["resolution"]))

print("[INFO] Kamera bemelegítése..")
time.sleep(conf["camera_warmup_time"])
avg = None
lastUploaded = datetime.datetime.now()
motionCounter = 0

for f in picamera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	
	frame = f.array
	timestamp = datetime.datetime.now()

	frame = imutils.resize(frame, width=500)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)
 
	if avg is None:
		print("[INFO] Háttér számolása..")
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue
 
	cv2.accumulateWeighted(gray, avg, 0.5)
	frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

	thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255,cv2.THRESH_BINARY)[1]
	thresh = cv2.dilate(thresh, None, iterations=2)
	cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
 
	
	for c in cnts:
		
		if cv2.contourArea(c) < conf["min_area"]:
			continue
 
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		
 
	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (0, 0, 255), 1)

	if conf["show_video"]:
		cv2.imshow("Security Feed", frame)
		key = cv2.waitKey(1) & 0xFF
 
		if key == ord("q"):
			break
 
	rawCapture.truncate(0)
