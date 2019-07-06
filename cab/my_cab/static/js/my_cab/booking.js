function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function getFormatDate(){
    var nowDate = new Date();
    var year = nowDate.getFullYear();
    var month = nowDate.getMonth() + 1 < 10 ? "0" + (nowDate.getMonth() + 1) : nowDate.getMonth() + 1;
    var date = nowDate.getDate() < 10 ? "0" + nowDate.getDate() : nowDate.getDate();
    var hour = nowDate.getHours()< 10 ? "0" + nowDate.getHours() : nowDate.getHours();
    var minute = nowDate.getMinutes()< 10 ? "0" + nowDate.getMinutes() : nowDate.getMinutes();
    var second = nowDate.getSeconds()< 10 ? "0" + nowDate.getSeconds() : nowDate.getSeconds();
    return year + "-" + month + "-" + date+" "+hour+":"+minute;
}


function showErrorMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function showResult(car_id){
    var begin_datetime = $("#dateSelect").val();
    var start_point = $('#startPoint').val();
    var end_point = $('#endPoint').val();

    if (begin_datetime && start_point && end_point){
        // alert(begin_datetime+start_point+end_point);
        $.get('/api/v1.0/order/distance?start_point='+start_point+'&end_point='+end_point, function (resp) {
            if (resp.errno == '0') {
                var distance = resp.data.distance;
                var duration = resp.data.duration;
                var price = $(".car-text>p>span").html();
                var amount = distance * parseFloat(price);
                var temp = '<div class="order-result">时长：'+ duration +'</div>\n' +
                    '       <div class="order-result">里程：' + distance + '公里</div>\n' +
                    '       <div class="order-result">费用：￥' + amount.toFixed(2) + '</div>';
                $('#order_result').append(temp);
                $('.submit-btn').on('click', function () {

                    $(this).prop('disabled', true);

                    var req_data = {
                        begin_date: begin_datetime,
                        start_point: start_point,
                        end_point: end_point,
                        duration: duration,
                        mileage: distance,
                        amount: amount,
                        car_id: car_id
                    };
                    var req_json = JSON.stringify(req_data);

                    $.ajax({
                        url: '/api/v1.0/order',
                        type: 'post',
                        data: req_json,
                        contentType: 'application/json',
                        dataType: 'json',
                        headers:{
                            "X-CSRFToken":getCookie("csrf_token")
                        },
                        success: function (resp) {
                            if (resp.errno == '0'){
                                location.href = '/orders.html'
                            }
                            else if (resp.errno == '4101'){
                                location.href = '/login.html'
                            }
                            else {
                                alert(resp.errmsg)


                            }
                        }

                    })
            


                })
            }
        });


    }
}


$(document).ready(function(){
    //验证登录
    $.get('/api/v1.0/session', function (resp) {
        if (resp.errno != '0') {
            location.href = '/login.html'
        }
    }, 'json');

    var result = decodeQuery();
    var car_id = result['cid'];
    var url = '/api/v1.0/order/booking/'+car_id;

    // alert(url);
    $.get(url, function (resp) {
        if (resp.errno == '0') {
            $('#car-info').html(template('car-temp', {car: resp.data.car}));
            $("#dateSelect").val(getFormatDate());
            $("#dateSelect").click(function () {
             var dtPicker = new mui.DtPicker({type: 'datetime', beginDate: getFormatDate()});

             /*参数：'datetime'-完整日期视图(年月日时分)
                     'date'--年视图(年月日)
                     'time' --时间视图(时分)
                     'month'--月视图(年月)
                     'hour'--时视图(年月日时)
             */
             dtPicker.show(function (selectItems) {
                 var y = selectItems.y.text;  //获取选择的年
                 var m = selectItems.m.text;  //获取选择的月
                 var d = selectItems.d.text;  //获取选择的日
                 var H = selectItems.h.text;  //获取选择的时
                 var M = selectItems.i.text;  //获取选择的分

                 var date = y + "-" + m + "-" + d + " " + H + ":" + M;
                 $("#dateSelect").val(date);
                 showResult(car_id);
             });

            });
            $('#startPoint').blur(function () {
             showResult(car_id);
            });
            $('#endPoint').blur(function () {
             showResult(car_id);
            })

        }
        else {
            alert(resp.errmsg)
        }
    });

    
});
