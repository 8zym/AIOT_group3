var lightChart = echarts.init(document.getElementById('lightChart'));

var option = {
    backgroundColor: 'rgba(1,202,217,.2)',
    grid: {
        left: 60,
        right: 50,
        top: 100,
        bottom: 50
    },
    title: {
        text: 'Real-time light intensity detection',
        top: 20,
        left: 'center',
        textStyle: {
            fontSize: 18,
            color: '#ffffff'
        }
    },
    xAxis: {
        name: 'time',
        type: 'category',
        axisLine: {
            lineStyle: {
                color: 'rgba(255,255,255,.2)'
            }
        },
        splitLine: {
            lineStyle: {
                color: 'rgba(255,255,255,.1)'
            }
        },
        axisLabel: {
            color: "rgba(255,255,255,.7)"
        },
        data: Array.from({ length: 30 }, (_, i) => i + 1),
        axisPointer: {
            type: 'shadow'
        }
    },
    yAxis: {
        type: 'value',
        name: 'light-intensity',
        axisLine: {
            lineStyle: {
                color: 'rgba(255,255,255,.3)'
            }
        },
        splitLine: {
            lineStyle: {
                color: 'rgba(255,255,255,.1)'
            }
        },
        axisLabel: {
            color: "rgba(255,255,255,.7)"
        },
        min: 0,
        max: 2000
    },
    series: [{
        name: 'light-intensity',
        type: 'line',
        data: [],
        smooth: true,
        itemStyle: {
            color: '#ff7f50',
            opacity: 0.8,
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowOffsetY: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
        },
        lineStyle: {
            width: 2
        }
    }]
};

lightChart.setOption(option);

var socketLight = new WebSocket('ws://192.168.71.242:6790');

socketLight.onmessage = function(event) {
    var data = JSON.parse(event.data);
    console.log("Received light intensity data:", data);

    updateLightChart(data.light);
};

function updateLightChart(newData) {
    var option = lightChart.getOption();
    option.series[0].data = newData.slice(0, 30); // Update with latest 30 data points
    lightChart.setOption(option);
}
