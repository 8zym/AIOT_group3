import serial
import time
import random
import json
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f'Failed to connect, return code {rc}')

def on_message(client, userdata, msg):
    print(f'Received {msg.payload.decode()} from {msg.topic}')
    
# initialize the serial port
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

try: 
    broker = 'y5a8f8af.ala.dedicated.gcp.emqxcloud.com'
    port = 1883
    topic= "/light_intensity"
    client_id = f'python-mqtt-{random.randint(0, 10000)}'
    username = 'pi1'
    password = 'raspberry'
    print(f'client_id={client_id}')
    # Set Connecting Client ID
    client = mqtt.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    client.loop_start()
    
    while True:
	    brightness = int(ser.readline().strip())
	    print(f'Received brightness data: {brightness}')
	    message = {"light_intensity": brightness}
	    json_message=json.dumps(message)
	    result = client.publish(topic, json_message)
	    time.sleep(0.5)
	    
except KeyboardInterrupt:
    print("Keyboard Interrupt detected. Exiting...") 
    
finally:
    ser.close()
    print("Serial port closed.")        
