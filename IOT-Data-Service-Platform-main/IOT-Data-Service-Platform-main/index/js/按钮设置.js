
/*var myChart = echarts.init(document.getElementById('aleftboxtbott'));
option = {
    color: ['#7ecef4'],
    backgroundColor: 'rgba(1,202,217,.2)',
    title: {
        top: 5,
        left: 20,
        textStyle: {
            fontSize: 10,
            color: 'rgba(255,255,255,.6)'
        },
        text: '环比类型：月环比'
    },
    legend: {
        right: 10,
        top: 5,
        textStyle: {
            fontSize: 10,
            color: 'rgba(255,255,255,.6)'
        },
        data: ['2023年3月', '2023年4月']
    },
    grid: {
        left: 20,
        right: 20,
        top: 30,
        bottom: 2,
        containLabel: true
    },

    xAxis: {
        type: 'value',
        axisLine: {
            lineStyle: {
                color: 'rgba(255,255,255,.2)'
            }
        },
        splitLine: {
            lineStyle: {
                color: 'rgba(255,255,255,0)'
            }
        },
        axisLabel: {
            color: "rgba(255,255,255,0)"
        },
        boundaryGap: [0, 0.01]
    },
    yAxis: {
        type: 'category',
    
        axisLine: {
            lineStyle: {
                color: 'rgba(255,255,255,.5)'
            }
        },
        splitLine: {
            lineStyle: {
                color: 'rgba(255,255,255,.1)'
            }
        },
        axisLabel: {
            color: "rgba(255,255,255,.5)"
        },
        data: ['用水量 (m³)', '用电量 (°)', '水费 (元)', '电费 (元)']
    },
    series: [{
        name: '2023年3月',
        type: 'bar',
        barWidth: 15,
        label: {
            show: true,
            position: 'inside'
        },
        itemStyle: {
            normal: {
                color: new echarts.graphic.LinearGradient(
                    1, 0, 0, 1, [{
                        offset: 0,
                        color: 'rgba(77,114,217,.7)'
                    }, {
                        offset: 1,
                        color: 'rgba(117,72,159,.7'
                    }]
                )
            }
        },
        data: [18203, 23489, 29034, 39098]
    }, {
        name: '2023年4月',
        type: 'bar',
        barWidth: 15,
        label: {
            show: true,
            position: 'inside'
        },
        itemStyle: {
            normal: {
                color: new echarts.graphic.LinearGradient(
                    1, 0, 0, 1, [{
                        offset: 0,
                        color: 'rgba(230,253,139,.7)'
                    }, {
                        offset: 1,
                        color: 'rgba(41,220,205,.7)'
                    }]
                )
            }
        },
        data: [19203, 24489, 30034, 40098]
    }]
};
myChart.setOption(option);*/

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
