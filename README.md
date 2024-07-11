# AIOT_group3
It's about faculty-driving detection project.

## Driver-Drowsiness-Detection

To run the project: python Driver Drowsiness Detection.py   

For environment: pip install -r Requirements.txt   

## Heart_rate_detection
original data in dir data

processed data in dir processed_data

combined final data in dir processed_final_data

main.py is the file for training K-means model

predict.py is the file for using K-means model to predict

other files are used for processing data

kmeans_model.pkl is the trained model
## weather_based_detection
TBC

## posture_based_analysis

To obtain the training and testing data, run unzip state-farm-distracted-driver-detection in data dir

The trained data is stored in saved_model dir

main.py is used for training data 

prediction.py is used for prediction

To apply the model in application, you need to some changes in prediction of the function form and file name.

# MQTT
## Personal WLAN Hot Post Config 

name: AIOTGroup3

password: asdfghjkl

## MQTT broker
EMQX in personal computer.

## MQTT client
+ Rpi1: Connects one Micro:bit used for light sensor and one R-pi camera used for posture recognition
+ Rpi2: Connects one Micro:bit used for display and one R-pi camera used for facial feature recognition
+ ESP32: Connects to a Temperature-Humidity sensor
+ PC: Serves as database and controller based on trained model
+ Web App: Serves as front end