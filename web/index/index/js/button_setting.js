

// 将滑块的当前值显示在旁边的文本中
function updateSliderValue(sliderId, valueId) {
    var slider = document.getElementById(sliderId);
    var value = document.getElementById(valueId);
    value.textContent = slider.value;
}

// 初始化滑块值显示
updateSliderValue('volume-slider', 'volume-value');
updateSliderValue('sensitivity-slider', 'sensitivity-value');

// 监听滑块变化事件
document.getElementById('volume-slider').addEventListener('input', function() {
    updateSliderValue('volume-slider', 'volume-value');
});

document.getElementById('sensitivity-slider').addEventListener('input', function() {
    updateSliderValue('sensitivity-slider', 'sensitivity-value');
});

// 监听LED和蜂鸣器开关按钮点击事件
document.getElementById('led-on-button').addEventListener('click', function() {
    // 执行开启LED的逻辑
    alert('开启LED');
});

document.getElementById('led-off-button').addEventListener('click', function() {
    // 执行关闭LED的逻辑
    alert('关闭LED');
});

document.getElementById('buzzer-on-button').addEventListener('click', function() {
    // 执行开启蜂鸣器的逻辑
    alert('开启蜂鸣器');
});

document.getElementById('buzzer-off-button').addEventListener('click', function() {
    // 执行关闭蜂鸣器的逻辑
    alert('关闭蜂鸣器');
});
