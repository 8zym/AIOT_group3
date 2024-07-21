import cv2
import socket
import base64
import numpy as np
import joblib
import dlib
import imutils
import pymysql
import pandas as pd
import json
import threading
import time
import requests
import paho.mqtt.client as mqtt
from scipy.spatial import distance as dist
from imutils import face_utils
from EAR import eye_aspect_ratio
from MAR import mouth_aspect_ratio
from HeadPose import getHeadTiltAndCoords

# MQTT Configuration
broker = 'y5a8f8af.ala.dedicated.gcp.emqxcloud.com'  # Replace with your MQTT broker address
port = 1883
topic = '/facial_picture'  # Replace with your desired topic
username = 'pi1'
password = 'raspberry'
client_id = 'picamera'

# Define MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

def on_message(client, userdata, msg):
    print("Received message: " + str(msg.payload))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1,client_id)
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 600)
client.loop_start()

# Load models
light_model = joblib.load('/root/AIOT/project/weather_based_detection/indoorlight_test/indoorlight_test/fatigue_regression_model.pkl')
environment_model = joblib.load('/root/AIOT/project/weather_based_detection/weather_test/weather_test/fatigue_detection_model.pkl')

# Global Variables Initialization
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

# Database Connection
db = pymysql.connect(
    host='47.121.193.122',
    user='root',
    password='123456',
    database='emqx_data',  # 指定数据库
    cursorclass=pymysql.cursors.DictCursor
)
cursor = db.cursor()

# Queries
query1 = 'SELECT * FROM temp_hum ORDER BY id DESC;'
query2 = 'SELECT * FROM light_intensity ORDER BY id DESC;'

# Dlib Face Detector
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./dlib_shape_predictor/shape_predictor_68_face_landmarks.dat')

# 2D 图像点
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

def light_predict_fatigue_score(illumination):
    sample_illumination = pd.DataFrame({'Illumination (lx)': [illumination]})
    predicted_fatigue_score = light_model.predict(sample_illumination)
    return predicted_fatigue_score[0]

def environment_predict_fatigue(temperature, humidity):
    sample = pd.DataFrame({'Temperature': [temperature], 'Humidity': [humidity]})
    prediction = environment_model.predict(sample)
    return prediction[0]

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

stream_url = "http://192.168.71.242:8000/stream.mjpg"

def fetch_and_process_stream(url):
    global running
    for frame in fetch_stream(url):
        if not running:
            break
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
    global COUNTER, TOTAL, mCOUNTER, mTOTAL, Roll, Rolleye, Rollmouth, Fatigue, old_TOTAL, old_mTOTAL, old_perclos_value, old_tit_degree
    try:
        if Roll == 0:
            cursor.execute(query1)
            results1 = cursor.fetchall()
            cursor.execute(query2)
            results2 = cursor.fetchall()
            
            temperature_value = results1[0]['temp']
            humidity_value = results1[0]['hum']
            light_value = results2[0]['light_intensity']
            print(temperature_value)
            print(humidity_value)
            print(light_value)
            
            temperature_fatigue_status = environment_predict_fatigue(temperature_value, humidity_value)
            light_fatigue_score = light_predict_fatigue_score(light_value)
            
            ratio = 1 - 0.1 * (light_fatigue_score / 10)
            EYE_AR_THRESH = ratio * EYE_AR_THRESH_basic

            if temperature_fatigue_status == "特别容易疲劳":
                FATIGUE_VALUE = FATIGUE_VALUE_BASIC * 0.9
            elif temperature_fatigue_status == "较容易疲劳":
                FATIGUE_VALUE = FATIGUE_VALUE_BASIC * 0.95
            else:
                FATIGUE_VALUE = FATIGUE_VALUE_BASIC

        if frame is not None:
            frame = imutils.resize(frame, width=320)
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
                    COUNTER += 1
                    Rolleye += 1
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        TOTAL += 1
                        COUNTER = 0
                        cv2.putText(frame, "Eyes Closed!", (500, 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    COUNTER = 0

                mouth = shape[49:68]
                mouthMAR = mouth_aspect_ratio(mouth)
                mar = mouthMAR
                mouthHull = cv2.convexHull(mouth)

                if mar > MOUTH_AR_THRESH:
                    mCOUNTER += 1
                    Rollmouth += 1
                    cv2.putText(frame, "Yawning!", (500, 450),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    if mCOUNTER >= MOUTH_AR_THRESH_FRAMES:
                        mTOTAL += 1
                        mCOUNTER = 0

                Roll += 1
                
                (head_tilt_degree, start_point, end_point, end_point_alt) = getHeadTiltAndCoords(size, image_points, 576)

                if head_tilt_degree:
                    cv2.putText(frame, 'Head Tilt Degree: ' + str(head_tilt_degree[0]), (170, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                if Roll == 150:
                    perclos = (Rolleye / Roll) + (Rollmouth / Roll) * 0.2
                    if perclos > FATIGUE_VALUE:
                        Fatigue = 1
                    
                    if old_mTOTAL == 0:
                        cyl_mTotal = cyl_Total = cyl_fatigue_value = cyl_angle = 0
                    else:
                        cyl_mTotal =  mTOTAL / old_mTOTAL 
                        cyl_Total =  TOTAL / old_TOTAL
                        cyl_fatigue_value = perclos / old_perclos_value 
                        cyl_angle = head_tilt_degree[0] / old_tit_degree

                    payload = {
                    "yawning_times": mTOTAL,
                    "wink_times": TOTAL,
                    "FATIGUE_VALUE_THREHOLD": FATIGUE_VALUE,
                    "EYE_AR_THRESH": EYE_AR_THRESH,
                    "MOUTH_AR_THRESH": MOUTH_AR_THRESH,
                    "perclos_value": perclos,
                    "head_tilt_degree": head_tilt_degree[0],
                    "Fatigue": Fatigue,
                    "cyl_yawn": cyl_mTotal,
                    "cyl_wink": cyl_Total,
                    "cyl_fatigue": cyl_fatigue_value,
                    "cyl_angle": cyl_angle,
                    "temperature": temperature_value,
                    "humidity": humidity_value,
                    "light": light_value
                    }

                    old_mTOTAL = mTOTAL
                    old_TOTAL = TOTAL
                    old_tit_degree = head_tilt_degree[0]
                    old_perclos_value = perclos

                    Roll = 0
                    Rolleye = 0
                    Rollmouth = 0
                    mTOTAL = 0
                    TOTAL = 0

                    payload_json = json.dumps(payload)
                    client.publish(topic, payload=payload_json, qos=0)

                if Fatigue == 1:
                    cv2.putText(frame, "Fatigue!", (800, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("Frame", frame)
            
            if cv2.waitKey(1) == 27:  # Press 'ESC' to exit
                global running
                running = False
                exit(-1)

    except socket.timeout:
        print("No data received. Waiting for data...")

    except Exception as e:
        print("Error decoding frame:", e)

running = True
thread = threading.Thread(target=fetch_and_process_stream, args=(stream_url,))
thread.start()

# Wait for the thread to complete
thread.join()

# Cleanup
cursor.close()
db.close()
client.loop_stop()
client.disconnect()
cv2.destroyAllWindows()
