const image_connectUrl = 'ws://y5a8f8af.ala.dedicated.gcp.emqxcloud.com:8083/mqtt';

const image_options = {
    keepalive: 60,
    clientId: 'mqttjs_' + Math.random().toString(16).substring(2, 8),
    clean: true,
    connectTimeout: 30 * 1000,
    username: 'mqtt_web', 
    password: 'mqtt_password', 
    reconnectPeriod: 1000,
}

const image_topic = '/WebSocket/image';
const image_qos = 0;

console.log('connecting mqtt client');
const image_client = mqtt.connect(image_connectUrl, image_options);

image_client.on('error', (err) => {
    console.log('Connection error: ', err);
    image_client.end();
});

image_client.on('reconnect', () => {
    console.log('Reconnecting...');
});

image_client.on('connect', () => {
    console.log('Client connected:' + image_client.options.clientId);

    image_client.subscribe(image_topic, { qos: 0 }, (error) => {
        if (error) {
            console.log('Subscribe error:', error);
            return;
        }
        console.log(`Subscribe to topic ${image_topic}`);
    });
});

image_client.on('message', (topic, message) => {
    console.log('Received Message: ' + message.toString() + '\nOn topic: ' + topic);
    
    try {
        const imageMessage = JSON.parse(message.toString());
        const { image_data, image_name, image_label, index, time} = imageMessage;

        const imgElement = document.getElementById('image');
        const timeElement = document.getElementById('time');
        const labelElement = document.getElementById('label');
        
        if (imgElement) {
            imgElement.src = `data:image/png;base64,${image_data}`;
            console.log(`Image updated`);
        } else {
            console.log('Element with id image not found');
        }

        if (timeElement) {
            timeElement.innerText = time;
            console.log(`Timestamp updated`);
        } else {
            console.log('Element with id time not found');
        }

        if (labelElement) {
            labelElement.innerText = image_label;
            console.log(`Label updated`);
        } else {
            console.log('Element with id label not found');
        }
        
    } catch (error) {
        console.log('Error parsing message:', error);
    }
});
