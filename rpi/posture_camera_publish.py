import time
import io
import paho.mqtt.client as mqtt
import json
import os
import struct
from picamera2 import Picamera2
from PIL import Image
import uuid
import base64

# MQTT settings
broker = 'y5a8f8af.ala.dedicated.gcp.emqxcloud.com'  # Replace with your MQTT broker address
port = 1883
topic = '/posture_camera'  # Replace with your desired topic
username = 'pi1'
password = 'raspberry'
client_id='picamera'

# Define MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print("Received message: "+str(msg.payload))

client = mqtt.Client(client_id)
client.username_pw_set(username, password)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 600)
client.loop_start()

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
print('Camera initialized and started')

try:
    while True:
        try:
            # Capture image
            print('Capturing image...')
            buffer = picam2.capture_array("main")
            print('Image captured successfully')
            
            # Convert the image to bytes using PIL
            stream = io.BytesIO()
            print('Converting image to bytes using PIL...')
            img = Image.fromarray(buffer)
            img.save(stream, format='JPEG')
            stream.seek(0)
            image_data = stream.read()
            print('Image converted to bytes successfully')
            filename=f"image_{uuid.uuid4()}.jpg"
            image_base64=base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                  "image_name":filename,
                  "image_data":image_base64
            }
            payload_json=json.dumps(payload)
            
            # Publish file header
            client.publish(topic, payload=payload_json, qos=0)
            print('Image published successfully')
            time.sleep(0.5)  # Ensure the header is sent first
            
        except Exception as e:
            print(f"Error during image capture or sending: {e}")

except KeyboardInterrupt:
    print("Capture interrupted")

finally:
    # Clean up resources
    picam2.close()
    client.loop_stop()
    client.disconnect()

print('Photos send end.')
print('Server is receiving, wait patiently please!')
