var tempHumChart = echarts.init(document.getElementById('tempHumChart'));

var option = {
    backgroundColor: 'rgba(1,202,217,.2)',
    grid: {
        left: 60,
        right: 50,
        top: 100,
        bottom: 50
    },
    title: {
        text: 'Real-time temperature \nand humidity detection',
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
    yAxis: [
        {
            type: 'value',
            name: 'temperature',
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
            max: 50
        },
        {
            type: 'value',
            name: 'humidity',
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
            max: 100
        }
    ],
    series: [
        {
            name: 'temperature',
            type: 'line',
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
            },
            yAxisIndex: 0,
            data: []
        },
        {
            name: 'humidity',
            type: 'line',
            smooth: true,
            itemStyle: {
                color: '#87CEFA',
                opacity: 0.8,
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowOffsetY: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)',
            },
            lineStyle: {
                width: 2
            },
            yAxisIndex: 1,
            data: []
        }
    ]
};

tempHumChart.setOption(option);

var socketTempHum = new WebSocket('ws://192.168.71.242:6791');

socketTempHum.onmessage = function(event) {
    var data = JSON.parse(event.data);
    console.log("Received temperature and humidity data:", data);

    updateTempHumChart(data.temp_hum);
};

function updateTempHumChart(newData) {
    var option = tempHumChart.getOption();
    option.series[0].data = newData.map(item => item.temperature).slice(0, 30); // Update temperature data
    option.series[1].data = newData.map(item => item.humidity).slice(0, 30);    // Update humidity data

    tempHumChart.setOption(option);
}
