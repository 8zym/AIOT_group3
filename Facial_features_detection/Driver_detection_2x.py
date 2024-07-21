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

# 创建UDP socket#!/usr/bin/env python
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

