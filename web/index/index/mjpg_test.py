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

# 定义 HTML 页面和静态文件夹的绝对路径
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

class StreamingHandler(server.BaseHTTPRequestHandler):
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
                        img_resized = cv2.resize(img, (800, 480))  # 调整视频流大小
                        _, frame = cv2.imencode('.jpeg', img_resized)
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

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

try:
    picam2 = Picamera2()
    picam2.configure(picam2.create_video_configuration(main={"size": (1280, 720)}))
    output = StreamingOutput()
    picam2.start_recording(JpegEncoder(), FileOutput(output), quality=Quality.VERY_HIGH)

    address = ('192.168.253.242', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()

finally:
    picam2.stop_recording()
