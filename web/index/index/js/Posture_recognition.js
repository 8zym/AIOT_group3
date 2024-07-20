
// 图片滚动播放
/*(function($) {
    $.fn.textSlider = function(options) {
        var defaults = { //初始化参数
            scrollHeight: 80,
            line: 4,
            speed: 'normal',
            timer: 2000
        };
        var opts = $.extend(defaults, options);
        this.each(function() {
            var timerID;
            var obj = $(this);
            var $ul = obj.children("ul");
            var $height = $ul.find("li").height();
            var $Upheight = 0 - opts.line * $height;
            obj.hover(function() {
                clearInterval(timerID);
            }, function() {
                timerID = setInterval(moveUp, opts.timer);
            });

            function moveUp() {
                $ul.animate({
                    "margin-top": $Upheight
                }, opts.speed, function() {
                    for (i = 0; i < opts.line; i++) { //只有for循环了才可以设置一次滚动的行数
                        $ul.find("li:first").appendTo($ul);
                    }
                    $ul.css("margin-top", 0);
                });
            };
            timerID = setInterval(moveUp, opts.timer);
        });
    };
})(jQuery)

$(function() {
    $(".left2_table").textSlider({
        line: 1
    });
})

/* 停车滚动条  html 日期变动 */



/*
// 获取智慧停车 列表 div → 日期 div
var childs = $('div.zhtc_table_li_content div:nth-child(2)');
$.each(childs, function(index, item) {
    // 当前时间
    // 变更日期
    var timeStr = moment()
        .set('minute', randomNum(1, 59))
        .set('second', randomNum(1, 59))
        .add(-index, 'hours')
        .format('YYYY-MM-DD HH:mm:ss');

    // 日期换行
    timeStr = timeStr.substring(0, 10) + '<br/>' + timeStr.substring(11);

    $(item).html(timeStr);
});
console.info(childs);
*/

$(document).ready(function() {
    function fetchRealTimePhotoAndInfo() {
        $.ajax({
            url: 'ws://y5a8f8af.ala.dedicated.gcp.emqxcloud.com:8083/mqtt/getPhotoAndInfo',  // 修改为与第二段相同的服务器地址和路径
            method: 'GET',
            success: function(data) {
                // 假设服务器返回的数据格式为 { photoUrl: "url", status: "状态" }
                $('#real-time-photo').attr('src', data.photoUrl);
                $('#status-label').text('疲惫状态: ', data.status);
            },
            error: function() {
                console.error('无法从服务器获取数据');
            }
        });
    }

    // 每隔5秒刷新一次照片
    setInterval(fetchRealTimePhotoAndInfo, 5000);

    // 初次加载照片
    fetchRealTimePhotoAndInfo();
});