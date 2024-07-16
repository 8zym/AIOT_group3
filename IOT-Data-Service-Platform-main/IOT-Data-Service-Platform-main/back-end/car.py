'''
from datetime import datetime, timedelta
import random

import serial
import re
import pymysql


# 生成随机车位id
def random_id():
    return random.randint(1, 24)

# 读串口数据
def read_serial():
    while True:
        data = ser.readline().decode('utf-8').rstrip()
        if data:
            print(data)

# 获取车位的可用状态
def get_available(id):
    select_is_available = f"""SELECT is_available FROM parking WHERE id = {id}"""
    try:
        cursor.execute(select_is_available)
        is_available = cursor.fetchone()[0]
        print(f"{select_is_available} 查询成功: is_available = {is_available}")
        return is_available
    except:
        print(f"{select_is_available} 查询失败")
        return -1


# 车位有车：车位状态改为无车，记录结束时间
def one(id):
    i = 0
    while True:
        data = ser.readline().decode('utf-8').rstrip()
        if data:
            match = re.search(r'a:(\d+), d:(\d+)', data)
            if match:
                analog_val = int(match.group(1))
                digital_val = int(match.group(2))
                print(f'Analog value: {analog_val}, Digital value: {digital_val}')
                if digital_val == 0:
                    i = i + 1
                    if i == 5:
                        print(f"{id}号车位的车主已经离开")
                        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print("end_time = " + end_time)
                        sql = f"""UPDATE parking SET is_available=0,end_time='{end_time}' WHERE id = {id}"""
                        try:
                            cursor.execute(sql)
                            db.commit()
                            print(f"{id} 写入 end_time = {end_time} 成功")
                        except:
                            db.rollback()
                            print(f"{id} 写入 end_time = {end_time} 失败")
                        break
    try:
        sql = f"""SELECT start_time, end_time ,total_time FROM parking WHERE id = {id}"""
        cursor.execute(sql)
        row = cursor.fetchone()
        if row is None:
            print("查询失败: 没有找到匹配的数据")
        else:
            start_time = row[0]
            end_time = row[1]
            total_time = row[2]
            hours, remainder = divmod(total_time, 60)
            minutes = remainder
            print(f"开始时间: {start_time}\n结束时间: {end_time}\n总时间:{hours} 小时 {minutes} 分钟\n")
    except Exception as e:
        print(str(e))
        print("查询失败: " + sql)
    return


# 车位无车：车位状态改为有车，记录开始时间
def zero(id):
    i = 0
    while True:
        data = ser.readline().decode('utf-8').rstrip()
        if data:
            match = re.search(r'a:(\d+), d:(\d+)', data)
            if match:
                analog_val = int(match.group(1))
                digital_val = int(match.group(2))
                print(f'Analog value: {analog_val}, Digital value: {digital_val}')
                if digital_val == 1:
                    i = i + 1
                    if i == 5:
                        print(f"{id}号车位的车主已经到达")
                        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ser.write("start".encode())  # 显示屏开始计时
                        print("start_time = " + start_time)
                        # 写入start_time之前要清空end_time和total_time
                        clean_sql = f"""UPDATE parking SET end_time=NULL,total_time=NULL WHERE id = {id}"""
                        insert_start_time_sql = f"""UPDATE parking SET is_available=1,start_time='{start_time}' WHERE id = {id}"""
                        try:
                            cursor.execute(clean_sql)
                            cursor.execute(insert_start_time_sql)
                            db.commit()
                            print(f"{id} 写入 start_time = {start_time} 成功")
                        except:
                            db.rollback()
                            print(f"{id} 写入 start_time = {start_time} 失败")
                            print("回滚成功")
                        break
    try:
        sql = f"""SELECT start_time FROM parking WHERE id = {id}"""
        cursor.execute(sql)
        row = cursor.fetchone()
        if row is None:
            print("查询失败: 没有找到匹配的数据")
        else:
            print(row)
            print(f"start_time = {row[0]}")
    except Exception as e:
        print(str(e))
        print("查询失败: " + sql)
    return


if __name__ == '__main__':
    try:
        # 打开数据库连接
        db = pymysql.connect(host='localhost',
                             user='root',
                             password='123456',
                             database='arduino', )
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()
        ser = serial.Serial('COM5', 9600, timeout=0.5)
        analog_val = 0
        digital_val = 0

        while True:
            print("---" * 20)
            id = random_id()  # 车位id
            is_available = get_available(id)  # 车位是否有车
            if is_available == 1:
                print(f'{id}号车位有车')
                one(id)
            else:
                print("---" * 20)
                print(f'{id}号车位无车')
                zero(id)

    except Exception as e:
        print(str(e))
    finally:
        db.close()
        ser.close()
'''

#!/usr/bin/env python
# -*- coding=utf-8 -*-

import cv2
import socket
import base64
import numpy as np
import dlib
import imutils
from scipy.spatial import distance as dist
from imutils import face_utils
from EAR import eye_aspect_ratio
from MAR import mouth_aspect_ratio
from HeadPose import getHeadTiltAndCoords
import time

IP = '0.0.0.0'
PORT = 5555

# 创建UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

# 初始化 dlib 的面部检测器（基于 HOG）和面部标志预测器
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./dlib_shape_predictor/shape_predictor_68_face_landmarks.dat')

# 设定参数
EYE_AR_THRESH = 0.25
MOUTH_AR_THRESH = 0.79
MOUTH_AR_THRESH_FRAMES = 3
EYE_AR_CONSEC_FRAMES = 3
COUNTER = 0  # 眨眼帧计数器
TOTAL = 0  # 眨眼总数
mCOUNTER = 0  # 打哈欠帧计数器
mTOTAL = 0  # 打哈欠总数
Roll = 0  # 整个循环内的帧次数
Rolleye = 0  # 循环内闭眼帧数
Rollmouth = 0  # 循环内打哈欠数
Fatigue = 0  # 疲劳状态

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

print("Listening for data...")

while True:
    data, _ = sock.recvfrom(65535)  # 接收数据
    print("Data received, size:", len(data))  # 打印接收到的数据大小
    try:
        img = base64.b64decode(data)
        npimg = np.frombuffer(img, dtype=np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        if frame is not None:
            # 进行图像处理
            frame = imutils.resize(frame, width=640)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            size = gray.shape
            rects = detector(gray, 0)

            for rect in rects:
                (bX, bY, bW, bH) = face_utils.rect_to_bb(rect)
                cv2.rectangle(frame, (bX, bY), (bX + bW, bY + bH), (0, 255, 0), 1)
                shape = predictor(gray, rect)
                shape = face_utils.shape_to_np(shape)

                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
                ear = (leftEAR + rightEAR) / 2.0

                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

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
                cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)
                cv2.putText(frame, "MAR: {:.2f}".format(mar), (650, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if mar > MOUTH_AR_THRESH:
                    mCOUNTER += 1
                    Rollmouth += 1
                    cv2.putText(frame, "Yawning!", (800, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    if mCOUNTER >= MOUTH_AR_THRESH_FRAMES:
                        mTOTAL += 1
                        mCOUNTER = 0

                Roll += 1

                if Roll == 150:
                    perclos = (Rolleye / Roll) + (Rollmouth / Roll) * 0.2
                    if perclos > 0.38:
                        Fatigue = 1

                    Roll = 0
                    Rolleye = 0
                    Rollmouth = 0

                for (i, (x, y)) in enumerate(shape):
                    if i == 33:
                        image_points[0] = np.array([x, y], dtype='double')
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 8:
                        image_points[1] = np.array([x, y], dtype='double')
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 36:
                        image_points[2] = np.array([x, y], dtype='double')
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 45:
                        image_points[3] = np.array([x, y], dtype='double')
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 48:
                        image_points[4] = np.array([x, y], dtype='double')
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    elif i == 54:
                        image_points[5] = np.array([x, y], dtype='double')
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)
                    else:
                        cv2.circle(frame, (x, y), 1, (0, 0, 255), -1)
                        cv2.putText(frame, str(i + 1), (x - 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

                # Draw the determinant image points onto the person's face
                for p in image_points:
                    cv2.circle(frame, (int(p[0]), int(p[1])), 3, (0, 0, 255), -1)

                (head_tilt_degree, start_point, end_point, end_point_alt) = getHeadTiltAndCoords(size, image_points, 576)
                cv2.line(frame, start_point, end_point, (255, 0, 0), 2)
                cv2.line(frame, start_point, end_point_alt, (0, 0, 255), 2)

                if head_tilt_degree:
                    cv2.putText(frame, 'Head Tilt Degree: ' + str(head_tilt_degree[0]), (170, 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Show fatigue warning if detected
                if Fatigue == 1:
                    cv2.putText(frame, "Fatigue!", (800, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Display the frame
            cv2.imshow("Frame", frame)
            
            if cv2.waitKey(1) == 27:  # Press 'ESC' to exit
                break

    except Exception as e:
        print("Error decoding frame:", e)

# Cleanup
cv2.destroyAllWindows()
sock.close()

