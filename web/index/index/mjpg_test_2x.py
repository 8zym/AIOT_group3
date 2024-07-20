import io
import logging
import socketserver
import cv2
import numpy as np
import os

from http import server
from threading import Condition
from picamera2.encoders import Quality
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import base64
import joblib
import dlib
import imutils
import pymysql
from scipy.spatial import distance as dist
from imutils import face_utils
import pandas as pd
from EAR import eye_aspect_ratio
import json
from MAR import mouth_aspect_ratio
from HeadPose import getHeadTiltAndCoords
import time
import random
import paho.mqtt.client as mqtt

image_points = np.array([
    (359, 391),  # Nose tip 34
    (399, 561),  # Chin 9
    (337, 297),  # Left eye left corner 37
    (513, 301),  # Right eye right corner 46
    (345, 465),  # Left Mouth corner 49
    (453, 469)  # Right mouth corner 55
], dtype="double")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

EYE_AR_THRESH = 0.25
MOUTH_AR_THRESH = 0.79
MOUTH_AR_THRESH_FRAMES = 3
FATIGUE_VALUE = 0.38
EYE_AR_CONSEC_FRAMES = 3
COUNTER = 0  
TOTAL = 0
mCOUNTER = 0 
mTOTAL = 0  
Roll = 0  
Rolleye = 0  
Rollmouth = 0  
Fatigue = 0  
old_TOTAL = 0
old_mTOTAL = 0
old_perclos_value = 0
old_tit_degree = 0


light_model = joblib.load('/home/pi2/video_transport/index/model/fatigue_regression_model.pkl')
environment_model = joblib.load('/home/pi2/video_transport/index/model/fatigue_detection_model.pkl')
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('/home/pi2/video_transport/index/model/shape_predictor_68_face_landmarks.dat')

def light_predict_fatigue_score(illumination):
    sample_illumination = pd.DataFrame({'Illumination (lx)': [illumination]})
    predicted_fatigue_score = light_model.predict(sample_illumination)
    return predicted_fatigue_score[0]

def environment_predict_fatigue(temperature, humidity):
    sample = pd.DataFrame({'Temperature': [temperature], 'Humidity': [humidity]})
    prediction = environment_model.predict(sample)
    return prediction[0]

PAGE_PATH = '/home/pi2/video_transport/index/index.html'
STATIC_PATH = '/home/pi2/video_transport/index'

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
            
class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            try:
                with open(PAGE_PATH, 'rb') as file:
                    content = file.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(404)
                self.end_headers()
                logging.error("Could not read index.html: %s", str(e))
        elif self.path.startswith('/css/') or self.path.startswith('/js/') or self.path.startswith('/img/'):
            file_path = os.path.join(STATIC_PATH, self.path[1:])
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as file:
                        content = file.read()
                    self.send_response(200)
                    if file_path.endswith('.css'):
                        self.send_header('Content-Type', 'text/css')
                    elif file_path.endswith('.js'):
                        self.send_header('Content-Type', 'application/javascript')
                    elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                        self.send_header('Content-Type', 'image/jpeg')
                    elif file_path.endswith('.png'):
                        self.send_header('Content-Type', 'image/png')
                    self.send_header('Content-Length', len(content))
                    self.end_headers()
                    self.wfile.write(content)
                except Exception as e:
                    self.send_error(404)
                    self.end_headers()
                    logging.error("Could not read static file %s: %s", file_path, str(e))
            else:
                self.send_error(404)
                self.end_headers()
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                        img = cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR)
                        img = cv2.resize(img, (800, 460)) 
                        if img is not None:
                            print(1)
                            frame = process_frame(img)
                            print(2)  
                            _, frame = cv2.imencode('.jpeg', frame)
                            print(3)
                            self.wfile.write(b'--FRAME\r\n')
                            self.send_header('Content-Type', 'image/jpeg')
                            self.send_header('Content-Length', len(frame))
                            self.end_headers()
                            self.wfile.write(frame)
                            self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def process_frame(frame):
    global Roll,Fatigue
    frame = imutils.resize(frame, width=800)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    size = gray.shape
    rects = detector(gray, 0)

    for rect in rects:
        (bX, bY, bW, bH) = face_utils.rect_to_bb(rect)
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)

        if ear < EYE_AR_THRESH:
            global COUNTER, Rolleye, TOTAL
            COUNTER += 1
            Rolleye += 1
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1
                COUNTER = 0
                cv2.putText(frame, "Eyes Closed!", (550, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            COUNTER = 0

        mouth = shape[49:68]
        mouthMAR = mouth_aspect_ratio(mouth)
        mar = mouthMAR
        mouthHull = cv2.convexHull(mouth)

        if mar > MOUTH_AR_THRESH:
            global mCOUNTER, Rollmouth, mTOTAL
            mCOUNTER += 1
            Rollmouth += 1
            cv2.putText(frame, "Yawning!", (50,20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            if mCOUNTER >= MOUTH_AR_THRESH_FRAMES:
                mTOTAL += 1
                mCOUNTER = 0

        Roll += 1

        if Roll == 150:
            perclos = (Rolleye / Roll) + (Rollmouth / Roll) * 0.2
            if perclos > FATIGUE_VALUE:
                Fatigue = 1

            Roll = 0
            Rolleye = 0
            Rollmouth = 0

        (head_tilt_degree, start_point, end_point, end_point_alt) = getHeadTiltAndCoords(size, image_points, 576)

        if head_tilt_degree:
            cv2.putText(frame, 'Head Tilt Degree: ' + str(head_tilt_degree[0]), (170, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if Fatigue == 1:
            cv2.putText(frame, "Fatigue!", (800, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    return frame

try:
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720)}))
    output = StreamingOutput()
    picam2.start_recording(JpegEncoder(), FileOutput(output), quality=Quality.HIGH)

    address = ('192.168.71.242', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()

finally:
    picam2.stop_recording()
