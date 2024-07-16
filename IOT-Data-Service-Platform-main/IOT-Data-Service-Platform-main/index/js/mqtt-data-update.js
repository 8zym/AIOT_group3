/**
 * 修改为你的云服务器的地址和端口
 */
const connectUrl = 'ws://192.168.71.159:8083/mqtt';

const options = {
    keepalive: 60,
    clientId: 'mqttjs_' + Math.random().toString(16).substring(2, 8),
    clean: true,
    connectTimeout: 30 * 1000,
    username: 'emqx_test', // 如果需要认证的话
    password: 'emqx_test', // 如果需要认证的话
    reconnectPeriod: 1000,
}

const topic = '/WebSocket/mqtt';
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
    document.getElementById('total-fatigue').innerText = data.totalFatigue;
    document.getElementById('blink-frequency').innerText = data.blinkFrequency;
    document.getElementById('yawn-count').innerText = data.yawnCount;
    document.getElementById('head-tilt').innerText = data.headTilt;
});
