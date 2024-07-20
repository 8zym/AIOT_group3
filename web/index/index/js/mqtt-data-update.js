/**
 * 修改为你的云服务器的地址和端口
 */
const connectUrl = 'ws://y5a8f8af.ala.dedicated.gcp.emqxcloud.com:8083/mqtt';

const options = {
    keepalive: 60,
    clientId: 'mqttjs_' + Math.random().toString(16).substring(2, 8),
    clean: true,
    connectTimeout: 30 * 1000,
    username: 'mqtt_web', // 如果需要认证的话
    password: 'mqtt_password', // 如果需要认证的话
    reconnectPeriod: 1000,
}

const topic = '/facial_picture';
const payload = 'WebSocket mqtt test'
const qos = 0

console.log('connecting mqtt client');
const client = mqtt.connect(connectUrl, options);

client.on('error', (err) => {
    console.log('Connection error: ', err);
    client.end();
});

client.on('reconnect', () => {
    console.log('Reconnecting...');
});

client.on('connect', () => {
    console.log('Client connected:' + client.options.clientId);

    client.subscribe(topic, { qos: 0 }, (error) => {
        if (error) {
            console.log('Subscribe error:', error);
            return;
        }
        console.log(`Subscribe to topic ${topic}`);
    });
});

client.on('message', (topic, message) => {
    console.log(
        'Received Message: ' + message.toString() + '\nOn topic: ' + topic
    );
    // 假设接收到的消息是一个JSON字符串，如：{"totalFatigue": 60, "blinkFrequency": 50, "yawnCount": 5, "headTilt": 3}
    const data = JSON.parse(message.toString());
    // ?? toFixed() ???????????
    const totalFatigue = (data.total_fatigue || 0).toFixed(3);
    const blinkFrequency = (data.blink_frequency || 0).toFixed(3);
    const yawnCount = (data.yawn_count || 0).toFixed(3);
    const headTilt = (data.head_tilt || 0).toFixed(3);

    // ?????????? HTML ???
    document.getElementById('total_fatigue').innerText = totalFatigue;
    document.getElementById('blink_frequency').innerText = blinkFrequency;
    document.getElementById('yawn_count').innerText = yawnCount;
    document.getElementById('head_tilt').innerText = headTilt;
});
