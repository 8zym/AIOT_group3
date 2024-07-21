#!/usr/bin/env python
# -*- coding=utf-8 -*-
import cv2
import socket
import base64
import numpy as np
import joblib
import dlib
import imutils
import pymysql
import sklearn
from scipy.spatial import distance as dist
from imutils import face_utils
import pandas as pd
from EAR import eye_aspect_ratio
import json
from MAR import mouth_aspect_ratio
from HeadPose import getHeadTiltAndCoords
import time
import random
import requests
import paho.mqtt.client as mqtt
import threading

def fetch_stream(url):
    stream = requests.get(url, stream=True)
    bytes = b''
    for chunk in stream.iter_content(chunk_size=1024):
        bytes += chunk
        a = bytes.find(b'\xff\xd8')
        b = bytes.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes[a:b+2]
            bytes = bytes[b+2:]
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
            yield img

stream_url = "http://192.168.66.242:8000/stream.mjpg"


def fetch_and_process_stream(url):
    for frame in fetch_stream(url):
        try:
            if frame is not None:
                process_frame(frame)
            elif frame is None:
                print("Frame is None")
        except socket.timeout:
            print("No data received. Waiting for data...")
            continue
        except Exception as e:
            print("Error decoding frame:", e)

def process_frame(frame):
    # 进行图像处理
    frame = imutils.resize(frame, width=320)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Display the frame
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == 27:  # Press 'ESC' to exit
        cv2.destroyAllWindows()

# 启动多线程处理视频流
thread = threading.Thread(target=fetch_and_process_stream, args=(stream_url,))
thread.start()
