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

$(document).ready(function(){
    // 检查用户的登录状态
    $.get("/api/v1.0/session", function (resp) {
        if ("4101" == resp.errno) {
            location.href = '/login.html'
        }
    });

    //获取区域数据
    //填充数据第一种方式
    // $.get('/api/v1.0/car/area', function (resp) {
    //     if (resp.errno == '0'){
    //         for (i=0;i<resp.data.length;i++){
    //             var area = resp.data[i];
    //             $('#area-id').append('<option value="' +area.area_id+'">'+area.area_name+'</option>')
    //         }
    //     }
    //     else {
    //         alert(errmsg)
    //     }
    // })

   // 填充数据第二种方式，使用art-template ，引入template.js
   $.get('/api/v1.0/car/area', function (resp) {
        if (resp.errno == '0'){
            var areas = resp.data;

        //    使用template.js的template(template, data)生成模板
            var html = template('area-temp', {areas:areas});
            $('#area-id').html(html)
        }
        else {
            alert(errmsg)
        }
    });

    //获取地址栏的房间id
    var result = decodeQuery();
    var car_id = result['id'];

    $.get('/api/v1.0/car/detail/'+car_id, function (resp) {
        if (resp.errno == '0') {
            // alert(resp.errmsg);
            var car = resp.data.car;
            $('#top-conn').html(template('top-temp', {car: car}));
            $('#middle-conn').html(template('middle-temp', {car: car}));

            //设置区域value
            $("#area-id").val(car.area_id);

            //获取配置数据
            $.get('/api/v1.0/car/facilities', function (resp) {
                if (resp.errno == '0') {
                    var facilities = resp.data;

                    //    使用template.js的template(template, data)生成模板
                    var html = template('facility-temp', {facilities: facilities});
                    $('.car-facility-list').html(html)

                    //遍历设置checkedbox
                    $.each(car.facilities, function (i, facility) {
                        $('input:checkbox[value="' + facility + '"]').prop('checked', true);
                    });

                } else {
                    alert(errmsg)
                }
            });
            $('#form-car-image').html(template('image-temp', {car: car}))

        } else {
            alert(resp.errmsg)
        }
    });


    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');





    //发送房屋信息参数
    $("#form-car-info").submit(function (e) {
        e.preventDefault();
        //获取房屋信息参数
        var raw_parm = $(this).serializeArray();
        var data = {};
        raw_parm.map(function (item) {
            data[item.name] = item.value
        });

        var car_id = $('#car-id').val();
        data['car_id'] = car_id;

        //获取房屋设施参数
        var facility = [];
        $(":checked[name=facility]").each(function (index, em) {
            facility[index] = $(em).val()
        });

        data["facility"] = facility;
        var req_json = JSON.stringify(data);
        // alert(req_json);
        $.ajax({
            url:'api/v1.0/car',
            type:'post',
            data: req_json,
            contentType: 'application/json',
            dataType: 'json',
            headers:{
                // 请求头，将csrf_token值放到请求中，方便后端csrf进行验证
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno == '4101'){
                    // alert(resp.errmsg);
                    location.href = '/login.html'
                }

                if (resp.errno == '0') {
                    $("#car-id").val(resp.data.car_id);
                    $("#form-car-info").hide();
                    $('#form-car-image').show();
                    alert(resp.errmsg)
                }
                else {
                    alert(resp.errmsg)
                }
            }

        })
    });

    $('#form-car-image').submit(function (e) {
        e.preventDefault();
        if ($('#car-image').val()) {

            $(this).ajaxSubmit({
                url: 'api/v1.0/car/image',
                type: 'post',
                dataType: 'json',
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                }, // 请求头，将csrf_token值放到请求中，方便后端csrf进行验证
                success: function (resp) {
                    if (resp.errno == '4101') {
                        alert(resp.errmsg);
                        location.href = '/login.html'
                    }

                    if (resp.errno == '0') {
                        alert(resp.errmsg);
                        var data = resp.data;

                        $('#car-image-cons').append('<img src="' + data.image_url + '">')
                    } else {
                        alert(resp.errmsg)
                    }
                }
            })
        }else {
            alert('请选择图片')
        }
    });



})