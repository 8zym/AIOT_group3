import cv2 
import dlib
import numpy as np
from scipy.spatial import distance as dist

# 计算眼睛的纵横比（Eye Aspect Ratio, EAR）
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# 初始化Dlib的人脸检测器和面部关键点预测器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# EAR阈值和连续帧数阈值
EAR_THRESHOLD = 0.25
CONSEC_FRAMES = 3
Tired_THRESHOLD = 20

# 初始化计数器和眨眼次数
counter = 0
total_blinks = 0
tired = 0

# 打开摄像头
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 0)

    for face in faces:
        shape = predictor(gray, face)
        shape = np.array([[p.x, p.y] for p in shape.parts()])

        left_eye = shape[36:42]
        right_eye = shape[42:48]

        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        if ear < EAR_THRESHOLD:
            counter += 1
            if counter > Tired_THRESHOLD:
                tired = 1
        else:
            if counter >= CONSEC_FRAMES:
                total_blinks += 1
            counter = 0

        # 在图像上绘制眼睛区域和EAR值
        for (x, y) in left_eye:
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        for (x, y) in right_eye:
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        if(tired == 1):
           cv2.putText(frame,f"You've been too tired!",(300,90),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,255,255),2)
        cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Blinks: {total_blinks}", (300, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
