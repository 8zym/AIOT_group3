#include <WiFi.h>
#include <PubSubClient.h>
#include <Arduino.h>
#include <Adafruit_Sensor.h>
#include "DHT.h"
#include <ArduinoJson.h> // 引入 ArduinoJson 库

// 定义温湿度传感器引脚
#define DHTTYPE DHT11   // DHT 11
#define DHTPIN 4        // 温湿度传感器引脚
#define photosensitivePin 18  // 光敏模块参数

// 温湿度传感器
DHT dht(DHTPIN, DHTTYPE);

// WiFi Credentials
const char *ssid = "AIOTGroup3";            // 替换为你的WiFi名称
const char *password = "asdfghjkl";         // 替换为你的WiFi密码

// MQTT Broker Settings
const char *mqtt_broker = "y5a8f8af.ala.dedicated.gcp.emqxcloud.com";
const char *mqtt_topic = "/temp_hum";
const char *mqtt_username = "esp32";
const char *mqtt_password = "esp32";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient mqtt_client(espClient);

// Function Declarations
void connectToWiFi();
void connectToMQTT();
void mqttCallback(char *mqtt_topic, byte *payload, unsigned int length);

void setup() {
    Serial.begin(115200);
    connectToWiFi();
    mqtt_client.setServer(mqtt_broker, mqtt_port);
    mqtt_client.setKeepAlive(60);
    mqtt_client.setCallback(mqttCallback); // Corrected callback function name
    connectToMQTT();
    dht.begin();  // 初始化温湿度传感器
}

void connectToWiFi() {
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi");
}

void connectToMQTT() {
    while (!mqtt_client.connected()) {
        String client_id = "esp32-client-" + String(WiFi.macAddress());
        Serial.printf("Connecting to MQTT Broker as %s.....\n", client_id.c_str());
        if (mqtt_client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
            Serial.println("Connected to MQTT broker");
        } else {
            Serial.print("Failed, rc=");
            Serial.print(mqtt_client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

void mqttCallback(char *mqtt_topic, byte *payload, unsigned int length) {
    Serial.print("Message received on mqtt_topic: ");
    Serial.println(mqtt_topic);
    Serial.print("Message: ");
    for (unsigned int i = 0; i < length; i++) {
        Serial.print((char) payload[i]);
    }
    Serial.println("\n-----------------------");
}

void loop() {
    // 检查 MQTT 连接状态
    if (!mqtt_client.connected()) {
        connectToMQTT();
    }
    mqtt_client.loop();
    
    // 读取温湿度数据
    double humidity = dht.readHumidity();
    double temperature = dht.readTemperature();
    
    // 检查是否成功读取数据
    if (isnan(humidity) || isnan(temperature)) {
        Serial.println(F("Failed to read from DHT sensor!"));
        return;
    }
    
    // 构建 JSON 对象
    StaticJsonDocument<32> doc;
    doc["temp"] = temperature;
    doc["hum"] = humidity;
    
    // 将 JSON 对象转换为字符串
    char jsonBuffer[256];
    serializeJson(doc, jsonBuffer);
    
    // 打印 JSON 数据（用于调试）
    Serial.print("Publishing JSON data: ");
    Serial.println(jsonBuffer);
    
    // 发布 JSON 数据到 MQTT 主题
    mqtt_client.publish(mqtt_topic, jsonBuffer);
    
    delay(5000); // 延迟五秒后重新读取温湿度数据
}
