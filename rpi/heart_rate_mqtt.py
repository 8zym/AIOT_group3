import RPi.GPIO as GPIO
import time
import random
import json
import paho.mqtt.client as mqtt

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic_subscribe)
    else:
        print(f'Failed to connect, return code {rc}')

def on_message(client, userdata, msg):
    global enable_doMeasureHeartRate
    print(f'Received {msg.payload.decode()} from {msg.topic}')
    enable_doMeasureHeartRate = bool(int(msg.payload.decode()))

def handle_heartrate(chl):
    global count
    global startTime

    count += 1
    currentTime = time.time()
    
    if currentTime - startTime > 15:
        if count > 0:
            heart_rate = count * 4
            message = {"heart_rate": heart_rate}
            json_message = json.dumps(message)  # Convert to JSON format
            print(f'Heart rate is {heart_rate}')
            result = client.publish(topic_publish, json_message)
            status = result[0]
            if status == 0:
                print(f"Sent `{json_message}` to topic `{topic_publish}`")
            else:
                print(f"Failed to send message to topic {topic_publish}")
        startTime = time.time()
        count = 0

# Pin definition
heartPin = 16
count = 0
startTime = time.time()
enable_doMeasureHeartRate = True

# Pin setup
GPIO.setmode(GPIO.BOARD)
GPIO.setup(heartPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print('Program running... Press Ctrl+C to exit')

try: 
    broker = 'y5a8f8af.ala.dedicated.gcp.emqxcloud.com'
    port = 1883
    topic_subscribe = "/enable_heartrate"
    topic_publish = "/heart_rate"
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

    GPIO.add_event_detect(heartPin, GPIO.RISING, callback=handle_heartrate)

    while True:
        time.sleep(0.2)

except KeyboardInterrupt:
    print('Program terminated!')
    
except OSError as err:
    print(f'An error has occurred: {err}')

finally:
    GPIO.cleanup()
