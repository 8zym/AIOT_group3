import time
import io
import paho.mqtt.client as mqtt
import os
import struct
from picamera2 import Picamera2
from PIL import Image

# MQTT settings
broker = '192.168.71.159'  # Replace with your MQTT broker address
port = 1883
topic = '/Group3/rpi2/camera'  # Replace with your desired topic

# Define MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print("Received message: "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 600)
client.loop_start()

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration( ))
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
            
            # Define file information. 128s indicates the filename is 128 bytes long, l indicates a long int for file size
            fileinfo_size = struct.calcsize('128sl')
            filename = 'image.jpg'
            filesize = len(image_data)
            fhead = struct.pack('128sl', bytes(filename.encode('utf-8')), filesize)
            
            # Publish file header
            print(f"Sending header for {filename} with size {filesize} bytes")
            client.publish(topic, payload=fhead, qos=0)
            time.sleep(1)  # Ensure the header is sent first
            
            # Publish image data in chunks
            chunk_size = 1024
            for i in range(0, filesize, chunk_size):
                chunk = image_data[i:i+chunk_size]
                client.publish(topic, payload=chunk, qos=0)
                print(f"Sent chunk {i//chunk_size + 1} of {filesize//chunk_size + 1}")
            
            print('Image sent successfully')
            time.sleep(0.5)  # Wait before capturing the next image

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
