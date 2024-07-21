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

broker = 'y5a8f8af.ala.dedicated.gcp.emqxcloud.com'  # Replace with your MQTT broker address
port = 1883
topic = '/facial_picture'  # Replace with your desired topic
username = 'pi1'
password = 'raspberry'
client_id='picamera'

# Define MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print("Received message: "+str(msg.payload))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,client_id)
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 600)
client.loop_start()

db = pymysql.connect(
    host='47.121.193.122',
    user='root',
    password='123456',
    database='emqx_data',  # 指定数据库
    cursorclass=pymysql.cursors.DictCursor
)

cursor = db.cursor()

query1 = 'SELECT * FROM temp_hum ORDER BY id DESC;'
query2 = 'SELECT * FROM light_intensity ORDER BY id DESC;'

# 设定参数
EYE_AR_THRESH_basic = 0.25
MOUTH_AR_THRESH = 0.79
MOUTH_AR_THRESH_FRAMES = 3
FATIGUE_VALUE_BASIC = 0.38
EYE_AR_CONSEC_FRAMES = 3
COUNTER = 0  # 眨眼帧计数器
TOTAL = 0  # 眨眼总数
mCOUNTER = 0  # 打哈欠帧计数器
mTOTAL = 0  # 打哈欠总数
Roll = 0  # 整个循环内的帧次数
Rolleye = 0  # 循环内闭眼帧数
Rollmouth = 0  # 循环内打哈欠数
Fatigue = 0  # 疲劳状态
old_TOTAL = 0 
old_mTOTAL = 0
old_perclos_value = 0
old_tit_degree = 0 

