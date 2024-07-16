from flask import Flask, render_template, Response
import cv2
import socket
import base64
import numpy as np
import dlib
import imutils
import sys
from scipy.spatial import distance as dist
from imutils import face_utils
sys.path.append('D:\新国立\IOT-Data-Service-Platform-main\Facial_features_detection')
from EAR import eye_aspect_ratio
from MAR import mouth_aspect_ratio
from HeadPose import getHeadTiltAndCoords
import time





app = Flask(__name__)

IP = '0.0.0.0'
PORT = 5556

# 创建UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))
sock.settimeout(1.0)  # 设置超时时间

# 初始化 dlib 的面部检测器（基于 HOG）和面部标志预测器
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('Facial_features_detection\dlib_shape_predictor\shape_predictor_68_face_landmarks.dat')

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

def generate_frames():
    while True:
        try:
            data, _ = sock.recvfrom(65535)  # 接收数据
            print("Data received, size:", len(data))  # 打印接收到的数据大小
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

                    if Roll == 150:
                        perclos = (Rolleye / Roll) + (Rollmouth / Roll) * 0.2
                        if perclos > 0.38:
                            Fatigue = 1

                        Roll = 0
                        Rolleye = 0
                        Rollmouth = 0

                    # Remove the following block to hide keypoints
                    """
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
                    """

                    # Draw the determinant image points onto the person's fa

                    (head_tilt_degree, start_point, end_point, end_point_alt) = getHeadTiltAndCoords(size, image_points, 576)

                    if head_tilt_degree:
                        cv2.putText(frame, 'Head Tilt Degree: ' + str(head_tilt_degree[0]), (170, 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    # Show fatigue warning if detected
                    if Fatigue == 1:
                        cv2.putText(frame, "Fatigue!", (800, 100),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                # 将处理后的帧转换为 JPEG 格式并返回
                ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        except socket.timeout:
            print("No data received. Waiting for data...")
            continue

        except Exception as e:
            print("Error decoding frame:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
