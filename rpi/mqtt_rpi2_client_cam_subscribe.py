import time
import io
import struct
import paho.mqtt.client as mqtt
from PIL import Image

# MQTT settings
broker = '192.168.71.159'  # Replace with your MQTT broker address
port = 1883
topic = '/Group3/rpi2/camera'  # Replace with your desired topic

# Variables to store incoming data
image_data = b''
file_size = 0
bytes_received = 0
header_received = False
image_count = 0  # Initialize the image counter

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)

# Callback when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    global image_data, file_size, bytes_received, header_received, image_count

    if not header_received:
        # Unpack the header to get the file size
        fileinfo_size = struct.calcsize('128sl')
        if len(msg.payload) == fileinfo_size:
            header = struct.unpack('128sl', msg.payload)
            file_size = header[1]
            print(f"Receiving file of size: {file_size} bytes")
            header_received = True
            image_data = b''
            bytes_received = 0
    else:
        # Append received chunk to image data
        image_data += msg.payload
        bytes_received += len(msg.payload)
        print(f"Received chunk: {bytes_received} of {file_size} bytes")

        # Check if the entire file has been received
        if bytes_received >= file_size:
            # Save the received data as an image file
            image_count += 1
            filename = f"image_{image_count}.jpg"
            print(f"Saving received image as {filename}...")
            image = Image.open(io.BytesIO(image_data))
            image.save(filename)
            print(f"Image saved as {filename}")
            # Reset for next image
            header_received = False
            image_data = b''
            file_size = 0
            bytes_received = 0

# Initialize the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 600)
client.loop_start()

try:
    # Keep the script running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    client.loop_stop()
    client.disconnect()
    print("Disconnected from broker")
