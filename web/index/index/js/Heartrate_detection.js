var heartRateChart = echarts.init(document.getElementById('heartRateChart'));

var option = {
    backgroundColor: 'rgba(1,202,217,.2)',
    grid: {
        left: 60,
        right: 50,
        top: 100,
        bottom: 50
    },
    title: {
        text: 'Real-time heart rate detection',
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
        name: 'heartrate',
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
        min: 50,
        max: 120
    },
    series: [{
        name: 'heartrate',
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

heartRateChart.setOption(option);

var socketHeartRate = new WebSocket('ws://192.168.71.242:6789');

socketHeartRate.onmessage = function(event) {
    var data = JSON.parse(event.data);
    console.log("Received heart rate data:", data);

    updateHeartRateChart(data.heart_rate);
};

function updateHeartRateChart(newData) {
    var option = heartRateChart.getOption();
    option.series[0].data = newData.slice(0, 30); // Update with latest 30 data points
    heartRateChart.setOption(option);
}

