import cv2
import socket
import base64
import numpy as np
import joblib
import dlib
import imutils
import pandas as pd
import time
import json
import random
import paho.mqtt.client as mqtt
from scipy.spatial import distance as dist
from imutils import face_utils
from EAR import eye_aspect_ratio
from MAR import mouth_aspect_ratio
from HeadPose import getHeadTiltAndCoords


IP = '0.0.0.0'
PORT = 5555

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))
sock.settimeout(1.0)

print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./dlib_shape_predictor/shape_predictor_68_face_landmarks.dat')

EYE_AR_THRESH_basic = 0.25
MOUTH_AR_THRESH = 0.79
MOUTH_AR_THRESH_FRAMES = 3
FATIGUE_VALUE_BASIC = 0.38
EYE_AR_CONSEC_FRAMES = 3
COUNTER = 0
TOTAL = 0
mCOUNTER = 0
mTOTAL = 0
Roll = 0
Rolleye = 0
Rollmouth = 0
Fatigue = 0

image_points = np.array([
    (359, 391),
    (399, 561),
    (337, 297),
    (513, 301),
    (345, 465),
    (453, 469)
], dtype="double")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


frame_count = 0
start_time = time.time()

while True:
    try:
        data, _ = sock.recvfrom(65535)
        img = base64.b64decode(data)
        npimg = np.frombuffer(img, dtype=np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        
        if frame is not None:
            frame = imutils.resize(frame, width=640)
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

                if ear < EYE_AR_THRESH:
                    COUNTER += 1
                    Rolleye += 1
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        TOTAL += 1
                        COUNTER = 0
                        cv2.putText(frame, "Eyes Closed!", (500, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    COUNTER = 0

                mouth = shape[49:68]
                mouthMAR = mouth_aspect_ratio(mouth)
                mar = mouthMAR

                if mar > MOUTH_AR_THRESH:
                    mCOUNTER += 1
                    Rollmouth += 1
                    cv2.putText(frame, "Yawning!", (500, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
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
                    cv2.putText(frame, 'Head Tilt Degree: ' + str(head_tilt_degree[0]), (170, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                if Fatigue == 1:
                    cv2.putText(frame, "Fatigue!", (800, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            frame_count += 1
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time
            print(f"FPS: {fps:.2f}")

            cv2.imshow("Frame", frame)
            
            if cv2.waitKey(1) == 27:
                break

    except socket.timeout:
        print("No data received. Waiting for data...")
        continue

    except Exception as e:
        print("Error decoding frame:", e)

cv2.destroyAllWindows()
sock.close()
