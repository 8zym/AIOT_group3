import time
import json
import random
import serial
import paho.mqtt.client as mqtt

global alarm_enable_flag

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)

# Callback when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    global alarm_enable_flag
    payload = msg.payload.decode()
    print("Received {} from {} topic".format(payload, msg.topic))
    data = json.loads(payload)
    alarm_enable_flag = data["alarm_enable"]

try:
    alarm_enable_flag = 0
    # Serial settings
    ser = serial.Serial('/dev/ttyACM1', 115200, timeout=1)

    # MQTT settings
    broker = 'y5a8f8af.ala.dedicated.gcp.emqxcloud.com'  # Replace with your MQTT broker address
    port = 1883
    topic = '/alarm_enable'  # Replace with your desired topic
    client_id = f'python-mqtt-{random.randint(0, 10000)}'
    username = 'pi2'
    password = 'raspberry'
    print('client_id={}'.format(client_id))

    # Initialize the MQTT client
    client = mqtt.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    client.loop_start()

    # Keep the script running
    while True:
        if ser.isOpen():
            if alarm_enable_flag == 1:
                alarm_enable_flag = 0
                ser.write('warning1$'.encode())
                print('Successfully sent warning1')
            elif alarm_enable_flag == 2:
                alarm_enable_flag = 0
                ser.write('warning2$'.encode())
                print('Successfully sent warning2')
        else:
            print('Failed to open serial port')
            time.sleep(1)

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    client.loop_stop()
    client.disconnect()
    print("Disconnected from broker")
    ser.close()
    print("Serial closed")
