# SMART DRIVER MONITER SYSTEM BASED ON IOT
--by SWS3025 Group3
---
Group3 Team members:
* ZHENG LIHAN (group leader)
* ZHENG YINGMING
* LI YINGZHUO
* MA MENGMENG
---
It's an faculty-driving detection project.

![AIoTGroup3 Portrait Poster (Template A1) pptx](https://github.com/user-attachments/assets/8f26c8a9-6ae5-43e2-af77-03144a16396e)

---
## HOW TO RUN THIS PROJECT
### HARDWARE
* Raspberry Pi *2
* ESP32
* Raspberry Pi Camera *2（Place one in front and the other on the side ）
* Sensors
  * Heartrate sensor
  * Temp and humidity sensor
  * Light sensor
* Steering wheel, toy or real

### SOFTWARE
#### Raspberry Pi 1
* posture_camera_publish.py
* heart_rate_mqtt.py
* light_detect_publish.py

#### Raspberry Pi 2
* mjpg_test.py
* index.html
* mqtt-data-update.js
* mqtt_image_update.js
* Heartrate_detection.py
* microbit_subscribe_final.py

#### ESP32
* temp_hum_detect.py

#### Micro:bit
* alarm_subscribe.js

## OVERVIEW OF PROBLEM STATEMENT
### DESCRIPTION OF PROBLEM
According to a survey by the American Foundation for Auto Traffic Safety, fatigued drivers account for up to 21 percent of traffic fatalities in the United States. To decline this proportion, Lots of researchers have focused on detecting fatigue driving in the past few decades, the latest progress includes active detection methods and passive detection methods. Among these methods, we are attracted by the active detection method based on facial features and driver posture. We want to use them as reference in combination with the AIoT.
### OVERVIEW OF SOLUTION PROBLEM
We are going to build a IoT-based Smart Driver Monitor System(DMS) to monitor the degree of fatigue by collecting multimodal sensor and camera data and transporting the data through the IoT system, using the AI and machine learning algorithms to analyze the data and train the model, giving reminders and warnings of fatigued driving through fronted applications so that the drivers can keep a sober mind and proper driving posture. We believe that DMS can fulfilling an important role in safe driving. In organisational context level, DMS can reduce the incidence of traffic accidents in the whole society. In consumer level, DMS would be the guarantee of driving safety.
![image](https://github.com/user-attachments/assets/b9683a95-9bcc-4d78-9dfa-948107383790)


## Driver-Drowsiness-Detection

I've uploaded all files used in project developing:

The files are listed as below:

|---- Driver Drowsiness Detection.py  # Original file in develop, using system camera to handle

|

|---- Driver detection 2x.py # edited files, using udp to translate camera theme from pi to backend

|

|---- Driver detection 4x.py # fetch screen from http, and try to connect with mqtt and mysql.

|

|---- Driver detection 5x.py # the final version, we will merge it with the code in pi2.

|

|---- EAR.py # functions relating to eye aspect ratio calculation

|

|---- HeadPose.py # functions relating to head tilt degree calculation

|

|---- MAR.py # functions relating to mouth aspect ratio calcuation

|

|---- Requirements.txt # The libraries needed

|

|---- ip_get.py # get the ip of computer 

|

|---- received_test.py # test files

|

|---- test.py # test files

|

|---- transform.py # useless files

|

|---- dlib_shape_predictor # The directory is imcomplete, you should download dlib model on your own
## Heart_rate_detection
data dir for original data

heart_rate_detection.2x dir is useless

model dir is for save trained models

processed_data dir is for saving data in process

processed_final_data is dir the final version of processed data

DBSCAN_pca.py / H_PCA.py / Hierachical_cluster.py / PCA.py / main.py are all for training models

DFAα1.py / LF_div_HF.py / LF_div_HF_new.py / SampEn.py / data.py / mean_RR.py  are all for data processing

predict.py are for predicting new data

heart_rate_detection_2x.py uses mysql for communicating with raspberry data 

## weather_based_detection

main.py is useless

files about indoor light simulation is in indoorlight_test dir

files about weather simulation is in weather_test dir

both dir contains data in training, training process, trained model and predict program.

## posture_based_analysis

(The data contains 4G, hard to upload, you can download through kaggle: kaggle competitions download -c state-farm-distracted-driver-detection(or through https://www.kaggle.com/competitions/state-farm-distracted-driver-detection/data)

weights_best_vanilla.keras is the trained model

main.py is used for training data 

prediction.py is used for prediction

poseture_based_analysis_2x.py connects with mysql and can communicate with raspberry pi data.

To apply the model in application, you need to some changes in prediction of the function form and file name.

## DETAILS ON IOT PROTOTYPE
![AIoTGroup3](https://github.com/user-attachments/assets/7d378fb6-1c7b-4956-97b1-59ff036c7f8d)

### MQTT
#### Why we use MQTT?
* MQTT is a publish-subscribe model which is ideal for one-to-many messaging

* MQTT is an extremely lightweight publish/subscribe messaging transport that is ideal for connecting remote devices with a small code footprint and minimal network bandwidth. So it is ideal for IoT System messaging.

* The MQTT broker is responsible for receiving all messages and sending them to the subscribed clients. So it is idel for extracting, filtering, enriching, and transforming data for further processing
#### Basic settings
MQTT Broker: EMQX in a dedicated cloud environment for business
MQTT Clients: 
Raspberry Pi
ESP32
Laptop used for AL and ML
Web Page
![image](https://github.com/user-attachments/assets/ce297575-03c4-442a-ab99-d0b80adb7a35)

#### EMQX rule engine
Rules were created for transmitting datas to SQL.
![image](https://github.com/user-attachments/assets/8735ba98-2ed3-48ac-9f46-08f88544e955)

![image](https://github.com/user-attachments/assets/00a07157-2cf5-419b-8487-b66cf75ac844)

#### Database: MySQL
We deployed a mysql database on a free AliCloud server and connected it to emqx's RULE ENGINE, which allows the mqtt broker to listen for messages on topics and store them in a corresponding table in the database for further processing.
![image](https://github.com/user-attachments/assets/9ad79046-13c0-4953-8fe2-de79409463b4)

#### MJPG—Streamer
In order to display face video images and detect them as smoothly as possible in real time, we choose to deploy mjpeg streamer on Raspberry Pi, which directly calls the camera to obtain mjpeg for processing, and at the same time calls the html, css and js files to be published on the specified port for network access.

### Personal WLAN Hot Post Config 

name: AIOTGroup3

password: asdfghjkl

## MQTT Broker
EMQX in personal computer.

## MQTT Client
+ Rpi1: Connects one Micro:bit used for light sensor and one R-pi camera used for posture recognition
+ Rpi2: Connects one Micro:bit used for display and one R-pi camera used for facial feature recognition
+ ESP32: Connects to a Temperature-Humidity sensor
+ Personal Laptop: Serves as database and controller based on trained model
+ Web App: Serves as front end
